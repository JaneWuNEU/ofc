"""Facilities for access and manipulation of FaaSLoad's database.

SQL queries:

 * `CREATE_TABLE_*`: create tables filled by the injector
 * `SELECT_COUNT_SELECT_COUNT_RUNS_INJECTOR`: count runs for a given injector
 * `DELETE_LOST_RUNS_INJECTOR`: delete runs that were not checkpointed for a given injector
 * `WIPE`: wipe all tables filled by the injector
 * `SELECT_FUNCTIONS`: select all functions in the functions table
 * `SELECT_FUNCTION_BY_NAME`: select a function by its partial name
 * `INSERT_PARTIAL_RUN`: insert partial data about a run
 * `INSERT_PARAMS`: insert parameter values of a run
 * `UPDATE_ACTIVATION`: update data about a run via its activation ID
 * `INSERT_RESOURCES`: insert resource usage data of a run

Table names are hardcoded in the queries:

 * "runs": general metadata about the runs
 * "parameters": parameter values of the runs
 * "resources": resource usage of the runs
 * "functions": functions to invoke in the runs

The table "functions" is prepared manually (see modules `functions`). "runs", "parameters" and "resources" are created
when initializing a `FaaSLoadDatabase` so their names should always be right.

Classes:

 * `FaaSLoadDatabase`: "client" to the database used by the dataset generator

Exceptions:

 * `FaaSLoadDatabaseException`: general exception wrapping the underlying mysql_connector exception
"""
from collections import namedtuple

import mysql.connector as dbc
import yaml

# activation_id is the ID given by OpenWhisk, so the activation can be obtained from it
# it's then a bit redundant to store start_ms, etc. but I prefer having all needed data in my DB
CREATE_TABLE_RUNS = """
CREATE TABLE IF NOT EXISTS `runs` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `function` BIGINT UNSIGNED NOT NULL,
    `namespace` VARCHAR(256),
    `activation_id` CHAR(32),
    `failed` BOOLEAN,
    `start_ms` BIGINT UNSIGNED,
    `end_ms` BIGINT UNSIGNED,
    `wait_ms` BIGINT UNSIGNED,
    `init_ms` BIGINT UNSIGNED,
    `outputsize` BIGINT UNSIGNED,
    `extract_ms` BIGINT UNSIGNED,
    `transform_ms` BIGINT UNSIGNED,
    `load_ms` BIGINT UNSIGNED,
    INDEX (`activation_id`),
    FOREIGN KEY `function_runs` (`function`) REFERENCES `functions` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT
)
"""

CREATE_TABLE_RESOURCES = """
CREATE TABLE IF NOT EXISTS `resources` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `run` BIGINT UNSIGNED NOT NULL,
    `timestamp_ms` BIGINT UNSIGNED NOT NULL,
    `memory_B` BIGINT UNSIGNED,
    `proc_mCPU` MEDIUMINT UNSIGNED,
    FOREIGN KEY `run_resources` (`run`) REFERENCES `runs` (`id`) ON UPDATE CASCADE ON DELETE CASCADE
)
"""

CREATE_TABLE_PARAMETERS = """
CREATE TABLE IF NOT EXISTS `parameters` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `run` BIGINT UNSIGNED NOT NULL,
    `name` VARCHAR(256) NOT NULL,
    `value` VARCHAR(2048),
    FOREIGN KEY `run_parameters` (`run`) REFERENCES `runs` (`id`) ON UPDATE CASCADE ON DELETE CASCADE
)
"""

SELECT_COUNT_RUNS_INJECTOR = """
SELECT COUNT(*) AS `count` FROM `runs`
WHERE `function` = %(function_id)s AND `namespace` = %(namespace)s
"""

DELETE_LOST_RUNS_INJECTOR = """
DELETE FROM `runs`
WHERE `function` = %(function_id)s AND `namespace` = %(namespace)s AND `id` > %(last_id)s
"""

WIPE = """
TRUNCATE TABLE `parameters`;
TRUNCATE TABLE `resources`;
TRUNCATE TABLE `runs`;
"""

SELECT_FUNCTIONS = """
SELECT `id`, `name`, `parameters`, `input_kind` FROM `functions`
"""

SELECT_FUNCTION_BY_NAME = """
SELECT `id`, `name`, `parameters`, `input_kind` FROM `functions`
WHERE `name` LIKE %(name_pattern)s
"""

INSERT_PARTIAL_RUN = """
INSERT INTO `runs` (
    `function`, `namespace`, `activation_id`
) VALUES (%(function_id)s, %(namespace)s, %(activation_id)s)
"""

INSERT_PARAMS = """
INSERT INTO `parameters` (`run`, `name`, `value`)
VALUES (%(run_id)s, %(name)s, %(value)s)
"""

UPDATE_ACTIVATION = """
UPDATE `runs`
SET
    `failed` = %(failed)s,
    `start_ms` = %(start)s,
    `end_ms` = %(end)s,
    `wait_ms` = %(wait_time)s,
    `init_ms` = %(init_time)s,
    `outputsize` = %(output_size)s,
    `extract_ms` = %(extract_time)s,
    `transform_ms` = %(transform_time)s,
    `load_ms` = %(load_time)s
WHERE `activation_id` = %(activation_id)s
"""

INSERT_RESOURCES = """
INSERT INTO `resources` (`run`, `timestamp_ms`, `memory_B`, `proc_mCPU`)
VALUES (
    (SELECT `id` FROM `runs` WHERE `activation_id` = %(activation_id)s),
    %(date)s,
    %(memory)s,
    %(cpu)s
)
"""

# Define our own namedtuple that can be pickled
# Namedtuples produced by mysqlconnector are created on-the-fly (because the columns are unknown), which makes them
# impossible to pickle. So I fix the expected columns in the queries SELECT_FUNCTION{,S} and as a namedtuple.
FunctionRecord = namedtuple('FunctionRecord', ['id', 'name', 'parameters', 'input_kind'])


class FaaSLoadDatabase:
    """Client facility to manipulate the database for the load injection.

    Upon initialization, it creates if needed, the tables filled by the injector: "runs", "parameters" and "resources".

    This class holds a connection and a cursor to the database, and provides high-level operations for the injector
    using this cursor. All the writing operations try to commit the transaction themselves, or rollback it upon failure,
    i.e. nothing is written or deleted, and the tables are left unchanged.
    """

    def __init__(self, cfg):
        """Initialize a new client to the database.

        :param cfg: the database configuration
        :type cfg: DatabaseConfiguration

        If `drop` is True, the tables "runs", "parameters" and "resources" are dropped before being recreated.
        """
        self.cnx = dbc.connect(**cfg._asdict())
        self.cur = self.cnx.cursor(named_tuple=True)

        self.cur.execute(CREATE_TABLE_RUNS)
        self.cur.execute(CREATE_TABLE_RESOURCES)
        self.cur.execute(CREATE_TABLE_PARAMETERS)

    def close(self):
        """Close the connection to the database.

        Do not use this instance after calling `close`.
        """
        self.cnx.close()

    def delete_lost_runs(self, state):
        """Delete lost runs, i.e. delete run records with IDs strictly greater than the last run of the injector states.

        :param state: states of injectors for which to delete lost runs
        :type state: list of InjectorState

        :raises FaaSLoadDatabaseException: the operation failed

        There is a security in this method that prevents its executions and raises in the case that more than 2 records
        would be deleted for a given injector. This is to prevent accidents like reloading an old state by mistake.
        """
        for inj_state in state:
            # security to avoid wiping the table on bad state reloading
            self.cur.execute(SELECT_COUNT_RUNS_INJECTOR, {
                'function_id': inj_state.trace_state.function.id,
                'namespace': inj_state.trace_state.user,
            })
            nb_runs = self.cur.fetchone().count
            if inj_state.last_run > nb_runs:
                raise FaaSLoadDatabaseException(
                    f'last run ID of injector of {inj_state.trace_state.function.name} of user '
                    f'{inj_state.trace_state.user} is greater than the number of runs of this injector (wrong state '
                    'restored?): aborting')
            if nb_runs - inj_state.last_run > 2:
                raise FaaSLoadDatabaseException(
                    f'deleting lost runs of injector of {inj_state.trace_state.function.name} of user '
                    f'{inj_state.trace_state.user} would delete more than 2 records: aborting')

            try:
                self.cur.execute(DELETE_LOST_RUNS_INJECTOR, {
                    'function_id': inj_state.trace_state.function.id,
                    'namespace': inj_state.trace_state.user,
                    'last_id': inj_state.global_last_run,
                })
                self.cnx.commit()
            except dbc.Error as err:
                self.cnx.rollback()
                raise FaaSLoadDatabaseException from err

    def wipe(self):
        """Wipe all tables filled by the injector: runs, parameters and resources.

        :raises FaaSLoadDatabaseException: the operation failed
        """
        try:
            self.cur.execute(WIPE)
            self.cnx.commit()
        except dbc.Error as err:
            self.cnx.rollback()
            raise FaaSLoadDatabaseException from err

    def select_functions(self):
        """Select all functions.

        :returns: the function records (nametuples)

        :raises FaaSLoadDatabaseException: the operation failed

        As a convenience, the field of parameters is parsed from its YAML string representation.
        """
        try:
            self.cur.execute(SELECT_FUNCTIONS)
            return [_function_row2namedtuple(func) for func in self.cur.fetchall()]
        except dbc.Error as err:
            raise FaaSLoadDatabaseException from err

    def select_function(self, func_name):
        """Select a function by its partial name.

        :param func_name: partial name of the function
        :type func_name: str

        :returns: the record of the function (a namedtuple)

        :raises FaaSLoadDatabaseException: more than one function matched the partial name, or the operation failed

        Allows to retrieve the function by name without specifying the package name. If the name is ambiguous because of
        multiple functions with the same name under different packages, raises an error.

        As a convenience, the field of parameters is parsed from its YAML string representation.
        """
        try:
            self.cur.execute(SELECT_FUNCTION_BY_NAME, {'name_pattern': f'%{func_name}'})
            results = self.cur.fetchall()
            if len(results) > 1:
                raise FaaSLoadDatabaseException(f'ambiguous function name {func_name}')
            result = results[0]
            return _function_row2namedtuple(result)
        except dbc.Error as err:
            raise FaaSLoadDatabaseException from err

    def insert_partial_run(self, run_data):
        """Store PARTIAL metadata about a run.

        :param run_data: the data of the run
        :type run_data: dict

        :returns: the ID of the newly inserted run in the table "runs"

        :raises FaaSLoadDatabaseException: the operation failed

        See `INSERT_PARTIAL_RUN` for the list of the fields expected in `run_data`.
        """
        try:
            self.cur.execute(INSERT_PARTIAL_RUN, run_data)
            self.cnx.commit()
        except dbc.Error as err:
            self.cnx.rollback()
            raise FaaSLoadDatabaseException from err

        return self.cur.lastrowid

    def insert_parameters(self, run_id, params):
        """Store parameter values of a run.

        :param run_id: the ID of the run which parameters are stored
        :type run_id: int
        :param params: the parameter values (see below)
        :type params: dict

        :raises FaaSLoadDatabaseException: the operation failed

        `params` is a dictionary mapping parameter names to their values.
        """
        try:
            for name, value in params.items():
                self.cur.execute(INSERT_PARAMS, {
                    'run_id': run_id,
                    'name': name,
                    'value': value,
                })
            self.cnx.commit()
        except dbc.Error as err:
            self.cnx.rollback()
            raise FaaSLoadDatabaseException from err

    def update_activation(self, act_id, run_data):
        """Store remaining metadata of a partial run.

        :param act_id: the activation ID of the run to complete
        :type act_id: str
        :param run_data: the complete data of the run
        :type run_data: dict

        """
        run_data['activation_id'] = act_id
        try:
            self.cur.execute(UPDATE_ACTIVATION, run_data)
            self.cnx.commit()
        except dbc.Error as err:
            self.cnx.rollback()
            raise FaaSLoadDatabaseException from err

    def insert_resources(self, act_id, res):
        """Store resource usage measurements of a run.

        :param act_id: the OpenWhisk activation ID of the run which resource usage measurements are stored
        :type act_id: str
        :param res: the resource usage measurements (see below)
        :type res: list

        :raises FaaSLoadDatabaseException: the operation failed

        `res` is a list of measurements. A measurement is a dictionary with the following fields:

          * date: the timestamp of the measurement, in seconds, rounded to the millisecond
          * memory: the measured memory usage, in bytes
          * cpu: the measured CPU usage, in CPU, rounded to the milliCPU
        """
        try:
            for meas in res:
                self.cur.execute(INSERT_RESOURCES, {
                    'activation_id': act_id,
                    'date': meas['date'] * 1000,
                    'memory': meas['memory'],
                    'cpu': meas['cpu'] * 1000,
                })
            self.cnx.commit()
        except dbc.Error as err:
            self.cnx.rollback()
            raise FaaSLoadDatabaseException from err


def _function_row2namedtuple(func_rec):
    return FunctionRecord(id=func_rec.id, name=func_rec.name, parameters=yaml.full_load(func_rec.parameters),
                          input_kind=func_rec.input_kind)


class FaaSLoadDatabaseException(Exception):
    """A database operation failed.

    Used as a wrapper around the low-level Error raised by the connector to MySQL databases.
    """
    pass
