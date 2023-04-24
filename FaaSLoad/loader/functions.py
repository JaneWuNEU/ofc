"""Facilities to import function (action) information in the database.

By calling `load_to_database(read_functions('path/to/manifest.yml'), db_cfg)`, you can import the actions that you
deployed to OpenWhisk (using wskdeploy) into the database, so the generator can know them and use them.

SQL queries:

 * `CREATE_TABLE`: create the table to import the functions
 * `INSERT_FUNCTION`: import one function into the database

Constants:

 * `LIMIT_NAMES`: a mapping between the limit names in the Manifest, and the names of the limit fields in an Action

Methods:

 * `read_functions`: read functions (as instances of Action) from the Manifest
 * `load_load_to_database`: load the Action instances into the database
"""

import logging

import mysql.connector as dbc
import yaml
from pywhisk.models import Action, ActionExec, ActionLimits

CREATE_TABLE = """
CREATE OR REPLACE TABLE `functions` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(256),
    `runtime` VARCHAR(64),
    `image` VARCHAR(256),
    `parameters` VARCHAR(2048),
    `input_kind` ENUM('audio', 'image', 'video'),
    INDEX (`name`)
)
"""

INSERT_FUNCTION = """
INSERT INTO `functions` (`name`, `runtime`, `image`, `parameters`, `input_kind`)
VALUES (%(name)s, %(runtime)s, %(image)s, %(parameters)s, %(input_kind)s)
"""


def read_functions(manifest_path):
    """Read functions from the Manifest.

    :param manifest_path: path to the Manifest
    :type manifest_path: str

    :return: dictionary mapping function names to Action

    `manifest_path` should point to the Manifest used to deploy actions in OpenWhisk using wskdeploy.
    """
    with open(manifest_path, 'r') as manifest_file:
        manifest = yaml.full_load(manifest_file)

    return {pkg_name + '/' + action_name: _compose_action(action_dict)
            for pkg_name, pkg_dict in manifest['packages'].items()
            for action_name, action_dict in pkg_dict['actions'].items()}


LIMIT_NAMES = {
    'memorySize': 'memory',
    'timeout': 'timeout',
    'logSize': 'logs',
    'concurrentActivations': 'concurrency',
}


def _compose_action(d):
    """Create an Action from the dictionary read from the Manifest.

    :param d: dictionary representing an action as loaded from the Manifest file
    :type d: dict

    :return: the Action

    **ONLY FITTING FOR MY MANIFEST FILE**
    """

    try:
        ex = ActionExec(kind=d['runtime'], binary=True)
    except KeyError:
        ex = ActionExec(kind='blackbox', binary=True, image=d['docker'])

    limits = ActionLimits.from_dict(
        {LIMIT_NAMES[limit_name]: limit_value for limit_name, limit_value in d['limits'].items()})

    return Action(exec=ex,
                  limits=limits,
                  annotations=[{'key': anno_name, 'value': anno_value} for anno_name, anno_value in
                               d['annotations'].items()])


def load_to_database(functions, db_cfg):
    """Load the functions to the database.

    :param functions: functions to load to database (mapping {name: Action})
    :type functions: dict[str, Action]
    :param db_cfg: configuration to connect to the database
    :type db_cfg: DatabaseConfiguration

    `functions` can be read from the Manifest using `read_functions()` and passed directly to this function.
    """
    logger = logging.getLogger('functionloader')

    functions_cnx = dbc.connect(**db_cfg._asdict())
    functions_cur = functions_cnx.cursor()
    functions_cur.execute(CREATE_TABLE)

    for function_name, function in functions.items():
        parameters = [a['value'] for a in function.annotations if a['key'] == 'parameters'][0]
        input_kind = [a['value'] for a in function.annotations if a['key'] == 'input_kind'][0]

        function_dict = {
            'name': function_name,
            'runtime': function.exec.kind,
            'image': function.exec.image if function.exec.kind == 'blackbox' else None,
            'parameters': yaml.dump(parameters),
            'input_kind': input_kind,
        }
        logger.debug('loading function %s: %s', function_name, function_dict)

        functions_cur.execute(INSERT_FUNCTION, function_dict)

    functions_cnx.commit()

    logger.info('loaded %d functions to database', len(functions))

    functions_cur.close()
    functions_cnx.close()


def basename(func_name):
    return func_name.split('/')[-1]
