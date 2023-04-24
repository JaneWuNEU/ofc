# Dataset generator mode

In dataset generator mode, FaaSLoad activates actions for every input listed in its configuration in order to produce a dataset of action activations.
This mode is very similar to the workload injector mode:
the difference is that FaaSLoad builds fake workload traces that make it run every action on every input (that is valid for this function, see ["FaaSLoad actions"](actions.md)).
Then, FaaSLoad runs those fake traces to invoke actions in OpenWhisk, and monitors their execution time, and more.
It uses the loader component to invoke actions in OpenWhisk;
the monitor can also be enabled to store memory and CPU usage of function invocations.

An addition in generator mode however, is the capability to checkpoint the dataset generation process in order to restart or prolong it in a reproducible way.

Sections below give setup, configuration and usage instructions for this usage mode.
["Output database structure"](dataset.md) gives a description of the resulting data as stored in the database.

Detailed documentations can be found in all Python modules and submodules; if you have troubles or questions relative to the loader or to the monitor, start by checking the docstrings in "loader/\_\_init\_\_.py" or "monitor/\_\_init\_\_.py".

## Setup

### Actions for dataset generation

Actions used in the dataset generation are read by FaaSLoad from the database.
They are loaded by reading a [Manifest file for `wskdeploy`](https://github.com/apache/openwhisk-wskdeploy) that describes them.
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

In addition, the generator activates actions via OpenWhisk users with predictable names (of the form "user-FUNCTION").
Those users must be created in OpenWhisk beforehand.
You can do that with the script in the folder "scripts" as shown below:

```shell
cd scripts
# Read action list from the DB and create corresponding users
./generator_create_users.sh
```

Then, you must load each user's action to its namespace. There is no script to do that, sorry!

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
Specifically for generation mode, first you must obviously enable the mode by setting `generation:enabled` to `true`.
Then, set the path to the directory where FaaSLoad will write it checkpoint states, under `generation:statedir`.
You can also leave the default value, but make sure the directory exists beforehand!

Finally, it is mandatory to set the number of inputs to use in generating the dataset, for each input kind.
For example:

```yaml
generation:
  nbinputs:
    image: 100
    audio: 100
    video: 100
```

Here, FaaSLoad will activate each action that processes images 100 times, each action that processes audio 100 times, etc.
See ["Fake workload traces for generator mode"](generation_traces.md) for more information about how FaaSLoad builds fake workload traces and activates actions in generator mode.

Moreover, using the monitor is enabled by default (you still have to start it yourself, as shown above).
It means that the loader will ask the monitor for CPU and memory usage of activated actions, and store it into the database.
See ["Docker monitor"](monitor.md) for more information about the Docker monitor component of FaaSLoad.

## Execution

The preferred way is to start its systemd unit as **a user unit**:

```shell
systemctl --user start faasload-loader.service
```

FaaSLoad will activate actions in OpenWhisk with the given inputs and parameters values chosen at random (see ["Fake workload traces for generator mode"](generation_traces.md)), and store activation data to its database (e.g. activation ID, parameters...).
When an activation is done, FaaSLoad will request full data (e.g. activation duration, byte size of the output...) and complete the activation data.
If the monitor is enabled, it will also store memory and CPU usage.

In case of failure, or user interruption with `systemctl --user stop faasload-loader`, the generator writes its checkpointed state to the configured folder. When restarted, it will find the latest checkpoint file and reload its state from it.

You can also run the generator manually with `python -m loader` from the virtualenv where you installed it.

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

To restart the generation at the point where it was interrupted, simply restart FaaSLoad:

```shell
systemctl --user start faasload-loader.service
```

Dataset generation will restart at the same point, with the same random state, to guarantee reproducibility of the dataset.

FaaSLoad restarts the generation when it finds a state file, so in order to restart from scratch:

 1. delete any "*.genstate" file in the folder specified in "loader.yml" under the setting `generation:statedir`
 2. save the content of the database and then `DROP` its `runs`, `resources` and `parameters` tables to provide a clean slate

## Troubleshooting

See ["Troubleshooting"](troubleshooting.md).