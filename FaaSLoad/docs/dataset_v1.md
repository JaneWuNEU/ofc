# Output database structure v1

_This document describes a past version of the structure of the dataset. Please refer to [dataset.md](dataset.md) for the current version._

The dataset is stored in a database (default name: `slimfaas`) in 7 interlinked tables:

 1. `runs`: records of the runs, the "main" table of the dataset;
 2. `functions`: records of the functions run to generate the database (referring actions in OpenWhisk via their names);
 3. `inputs_audio`, `inputs_image`, `inputs_video`: data used as input to the functions executed when generating the dataset (the table is selected depending on the function's input kind);
 4. `parameters`: parameters of function invocations in the runs;
 5. `resources`: resource usage measurements of the runs.

In load injector mode, the `inputs_KIND` tables are not required and may not be present. Moreover, the table `resources` is filled with data from the monitor component, which may be disabled.

_In particular, the monitor is not enabled when running in load injector mode; there is only a technical reason for this, and that could change in the future._

## Exploitation

To explore the dataset, you can start with a run from the table `runs`. A row includes the ID of the function (foreign key to `functions`) under the field `function`, and the ID of the input in the table of its kind under the field `input`; you can identify the corresponding input table with the field `input_kind` of the function.

The field `namespace` of the table `runs` gives the name of the user that ran the function. Note that in injector mode, the function stored in the database is a generic representation not linked to the user that invoked it. You must request OpenWhisk to retrieve information about the actual function that was invoked, with `wsk -u USER_AUTH action get FUNCTION_NAME`.

You can get the values of the parameters passed to this function invocation by selecting rows in `parameters`, by matching the run ID with the field `run` (a many-to-one key). Finally, if available, you can match the run ID with the field `run` in `resources` to select rows of resource usage measurements for this invocation.

The fields of all the tables are detailed next. The formal table definitions can be found as SQL statements named `CREATE_*` in sub-modules of `dataset_generator`: `functions` for `functions`, `inputs` for `inputs_KIND` and `database` for `runs`, `parameters` and `resources`.

### Table `functions`

| Name | Type | Description | Referenced by | Reference to |
|---|---|---|---|---|
| id | integer | index | runs.function |  |
| name | string | function name as declared in OpenWhisk |  |  |
| runtime | string | runtime name as declared in OpenWhisk |  |  |
| image | string | Docker image name if runtime is "blackbox", otherwise `NULL` |  |  |
| parameters | string | definition of function parameters (YAML) |  |  |
| input_kind | enum('audio', 'image', 'video') | kind of input | | |

### Tables `inputs_KIND`

The actual fields in the tables `input_KIND` may vary, but they must at least have the fields `id`, `container` and `object`, with `id` used as an internal index, and `container` and `object` names to fetch the actual input file from the Swift storage.

#### Table `inputs_image`

| Name | Type | Description | Referenced by | Reference to |
|---|---|---|---|---|
| id | integer | index | runs.input |  |
| original_id | integer | index in the source of the input dataset |  |  |
| url | string | URL to the input image |  |  |
| title | string | title of the input image |  |  |
| size_B | integer | size in bytes of the input image |  |  |
| base64md5 | string | Base64-encoded MD5 hash of the input image |  |  |

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
| input | integer | input index |  |  inputs_KIND.id |
| outputsize | integer | size of the output of the function in bytes |  |  |
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
