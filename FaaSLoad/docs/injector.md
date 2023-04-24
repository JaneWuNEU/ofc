# Workload injector mode

In workload injector mode, FaaSLoad runs traces describing serverless functions invocations of many users in OpenWhisk, and monitors their execution time, and more.
It reads the traces, and uses the loader component to invoke actions in OpenWhisk;
the monitor can also be enabled to store memory and CPU usage of function invocations.

Sections below give setup, configuration and usage instructions for this usage mode.
["Output database structure"](dataset.md) gives a description of the resulting data as stored in the database.

Obviously, you need workload traces describing the workload to inject.
The expected trace format is described in ["Injection traces"](injection_traces.md).
In the same document, you will find instructions on how to set up OpenWhisk actions, users and data storage to be used when injection the workload.

Detailed documentations can be found in all Python modules and submodules; if you have troubles or questions relative to the loader or to the monitor, start by checking the docstrings in "loader/\_\_init\_\_.py" or "monitor/\_\_init\_\_.py".

## Setup

### Injection traces

The document ["Injection traces"](injection_traces.md) explains what should be set up for FaaSLoad, in accordance with the workload traces:

 * injection users to activate actions, created in OpenWhisk;
 * actions deployed in OpenWhisk under the correct user namespaces;
 * data input loaded in the storage.

Following this, FaaSLoad needs two things:

 1. authentication tokens of injection users;
 2. metadata of actions.

Authentication tokens are read by FaaSLoad from a directory specified in its configuration (`openwhisk:authkeys`, see next section).
In the case of action metadata, they must be loaded in FaaSLoad's database for quick access, and also to link runs stored by FaaSLoad to the actions.

Actions are loaded by reading a [Manifest file for `wskdeploy`](https://github.com/apache/openwhisk-wskdeploy) that describes them.
An example can be found in the [repository of example actions for FaaSLoad](https://gitlab.com/faasload/actions).
There is some helper code in the `loader` module, and its usage is described below.

Spawn a Python interpreter in the virtualenv using `pipenv run python`, and then:

```python
from loader import DatabaseConfiguration, functions

# configuration to access the database, adapt it
db_cfg = DatabaseConfiguration(
    user='faasload',
    password='',
    database='faasload',
)

# load the functions
functions.load_to_database(functions.read_functions(f'path/to/manifest.yml'), db_cfg)
```

This creates and fills the table `functions` in the database.
Refer to ["Output database structure"](dataset.md) for details on this table and its link to other tables of the dataset produced by FaaSLoad.

### Monitor

As you know, you can optionally run the Docker monitor (see ["Docker monitor"](monitor.md) for more information).
Doing so requires a bit of setup with OpenWhisk: after starting the monitor, restart OpenWhisk's invoker component as shown below.

```shell
# Start the monitor
systemctl --user start faasload-monitor.service
# Restart the invoker
cd openwhisk/ansible
# Note the environment parameter user_events (see below)
ansible-playbook invoker.yml -e user_events=true
```

Specifying `-e user_events=true` is important:
it enables sending user events messages on Kafka's queues, which are used by FaaSLoad to receive notifications when action activations terminate.

## Configuration

The document ["Install FaaSLoad"](installation.md) told you to set a few settings.
Specifically for injector mode, you must set `injection:tracedir`:
this is the path to the directory where FaaSLoad will read workload traces.

Moreover, using the monitor is enabled by default (you still have to start it yourself, as shown above).
It means that the loader will ask the monitor for CPU and memory usage of activated actions, and store it into the database.
See ["Docker monitor"](monitor.md) for more information about the Docker monitor component of FaaSLoad.

## Execution

The preferred way is to start its systemd unit as **a user unit**:

```shell
systemctl --user start faasload-loader.service
```

FaaSLoad will read workload traces from the specified directory (see above), activate actions in OpenWhisk as requested, with the parameters given by the traces, and store activation data to its database (e.g. activation ID, parameters...).
When an activation is done, FaaSLoad will request full data (e.g. activation duration, byte size of the output...) and complete the activation data.
If the monitor is enabled, it will also store memory and CPU usage.

Note that, in opposition to the dataset generator mode, **there is no checkpointing**:
it makes no sense because the actual state of OpenWhisk would be lost anyway.

You can also run the injector manually with `python -m loader` from the virtualenv where you installed it.

### Execution Monitoring

Logging is based on the `logging` module of the Python standard library.
The configuration is given by the section `logging` in "loader.yml";
refer to [the logging module documentation](https://docs.python.org/3/library/logging.html#module-logging) for more information.
By default, tt is set to log to stderr, so using the systemd units is better, and you can read the logs using `journalctl`:

```shell script
# logs of the loader
# replace -e with -f to follow the logs as they arrive (like tail -f)
journalctl --user -eu faasload-loader
```

Set `logging:root:level` to `DEBUG` to increase logging verbosity, or to `WARNING` to decrease it, from the default level of `INFO`.

### Execution restart

If you want to run FaaSLoad again, save the content of the database and then `DROP` its `runs`, `resources` and `parameters` tables to provide a clean slate.

Depending on your experiment, you may want to restart OpenWhisk entirely (make sure to follow instructions in ["Install FaaSLoad"](installation.md) again, in particular for OpenWhisk's invoker in relation with the Docker monitor) to make sure it is "cold".

## Troubleshooting

See ["Troubleshooting"](troubleshooting.md).