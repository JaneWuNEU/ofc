# Output database structure

## Overview

Whether in injection or generation mode, the resulting dataset is stored in a database (see "config/loader.yml", section `database` for the default user and database names) in 4 interlinked tables:

 1. `runs`: records of the runs, the "main" table of the dataset;
 2. `functions`: records of the functions run to generate the database (referring to actions in OpenWhisk via their names, ignoring namespace and package);
 4. `parameters`: parameters of function invocations in the runs;
 5. `resources`: resource usage measurements of the runs.

The table `resources` is filled with data from the Docker monitor component **which you may have disabled**, so it can remain empty. See "Configuration" in [injector.md](injector.md) or in [generator.md](generator.md) for more information about enabling the Docker monitor.

## Exploitation

To explore the dataset, you can start with a run from the table `runs`. A row includes the ID of the function (foreign key to `functions`) under the field `function`. The field `namespace` of the table `runs` gives the name of the user that ran the function.

Note that the function stored in the table `functions` is a generic representation not linked to the user that invoked it. You must request OpenWhisk to retrieve information about the actual function that was invoked, with `wsk -u USER_AUTH action get FUNCTION_NAME`. See "OpenWhisk setup" in [injector.md](injector.md) or in [generator.md](generator.md) for information about how OpenWhisk users and their authentications are created.

You can get the values of the parameters passed to this function invocation by selecting rows in `parameters`, by matching the run ID with the field `run`. In particular, all runs should have at least the three following parameters:

 * `object`: the filename of this run's input on the input storage;
 * `incont`: the name of the container of this run's input on the input storage;
 * `outcont`: the name of the container of this run's output on the output storage.

See "Storage setup" in [injector.md](injector.md) or in [generator.md](generator.md) for more information about the storage of run inputs and outputs.

Finally, if available (i.e., if the monitor was enabled) you can match the run ID with the field `run` in `resources` to select rows of resource usage measurements for this invocation.

## Tables

The fields of all the tables are detailed below. The formal table definitions can be found as SQL statements named `CREATE_*` in `loader/functions` for the `functions` table, and in `loader/database` for the three other tables.

### Table `functions`

| Name | Type | Description | Referenced by | Reference to |
|---|---|---|---|---|
| id | integer | index | runs.function |  |
| name | string | function name as declared in OpenWhisk |  |  |
| runtime | string | runtime name as declared in OpenWhisk |  |  |
| image | string | Docker image name if runtime is "blackbox", otherwise `NULL` |  |  |
| parameters | string | definition of function parameters (YAML string) |  |  |
| input_kind | enum('audio', 'image', 'video') | kind of input | | |

### Table `runs`

| Name | Type | Description | Referenced by | Reference to |
|---|---|---|---|---|
| id | integer | index | parameters.run, resources.run |  |
| function | integer | function index |  |  functions.id |
| namespace | string | user owner of the function | | |
| activation_id | string | internal activation ID for OpenWhisk |  |  |
| failed | boolean | whether the run failed |  |  |
| start_ms | integer | start date of the run as a timestamp in milliseconds |  |  |
| end_ms | integer | end date of the run as a timestamp in milliseconds |  |  |
| wait_ms | integer | wait time of the run between invocation and execution start in milliseconds |  |  |
| init_ms | integer | initialization time of the runtime for the run in milliseconds if it was a cold start, `NULL` otherwise |  |  |
| outputsize | integer | size of the processed output of the function in bytes |  |  |
| extract_ms | integer | duration of the extract phase in milliseconds | | |
| transform_ms | integer | duration of the transform phase in milliseconds | | |
| load_ms | integer | duration of the load phase in milliseconds | | |

### Table `parameters`

| Name | Type | Description | Referenced by | Reference to |
|---|---|---|---|---|
| id | integer | index |  |  |
| run | integer | run index  |  | runs.id |
| name | string | name of the parameter |  |  |
| value | string | generated value of the parameter |  |  |

### Table `resources`

| Name | Type | Description | Referenced by | Reference to |
|---|---|---|---|---|
| id | integer | index |  |  |
| run | integer | run index |  | runs.id |
| timestamp_ms | integer | timestamp of the resource usage measurement in milliseconds |  |  |
| memory_B | integer | memory usage of the function as this date in bytes |  |  |
| proc_mCPU | integer | cumulated CPU usage of the function in mCPU |  |  |
