# Troubleshooting

As explained above, FaaSLoad's logs, when run as a systemd service, can be read using `journalctl --user -eu faasload-loader`.

## General problems

The documentation advise you to run FaaSLoad components (loader and monitor) as systemd user service units.
When running in an SSH session on a remote server, thos units are killed when you leave the session.
A solution is to enable lingering processes of systemd with the following command:

```shell
sudo loginctl enable-linger $USER
```

## FaasLoad problems

### FaasLoad hangs after loading the workload / generating the dataset

FaaSLoad waits for invocations to terminate, before requesting complete data about them from OpenWhisk.
Waiting for invocations is done by receiving notifications from OpenWhisk's Kafka queues.
Actually, notifications are sent by the invoker, but it requires running OpenWhisk's invoker with its Ansible playbook and a environment parameter define, calle `user_events`.
So, if the problem is indeed that notifications about action activations are not sent, you must restart OpenWhisk's invoker like this:

```shell
cd openwhisk/ansible
ansible-playbook invoker.yml -e user_events=true
```

### Monitor fails fetching resource usage

FaaSLoad may fail fetching resource usage from its monitor.
In turn, it may be that the monitor itself fail monitoring OpenWhisk's Docker container.
To check this hypothesis, look at the monitor's logs with the following command:

```shell
journalctl --user -eu faasload-monitor
```

You may see logs about receiving requests about unknown containers.
it means that, indeed, the monitor fails being notified about containers to monitor.

The reason may be that the UNIX socket it uses to receive notifications from OpenWhisk's invoker has not been mounted into the invoker's own Docker container (see ["FaaSLoad monitor"](monitor.md) for more information about how the Docker monitor works).
To fix this issue, run the following commands:

```shell
# Running the invoker may have created directories with the names of the sockets it tried to mount, so delete them
sudo rm -rf /run/wdm/*
# Make sure the user you run FaaSLoad as, has rights on the folder of the sockets
sudo chown $USER /run/wdm
# Restart OpenWhisk's invoker; don't forget to enable user_events as shown above!
cd openwhisk/ansible
ansible-playbook invoker.yml -e user_events=true
```

You should also check that no pre-warm containers of OpenWhisk actions are left running: the monitor can only monitor Docker containers of which it received a notification of creation.

## Python-related problems

If FaaSLoad fails to start, check the pipenv environment where you should have installed everything (see ["Install FaaSLoad"](installation.md)).

For instance, you can try the following commands:

```shell
# Navigate to FaaSLoad's installation directory
cd faasload
# Spawn a new shell in pipenv's virtual environment
pipenv shell
# Check the installed dependencies to verify none is missing (note the command "pip", not "pipenv")
pip list
# Run Python interactively
python
```

Now you are in Python's REPL.
For example, you can try to import FaaSLoad' modules:

```python
import loader, monitor

print(loader)
print(monitor)
```

## OpenWhisk-related problems

If FaaSLoad runs fine, but fails activating actions, it may be related to either a non working OpenWhisk installation, or to non working actions.
For both cases, try to list actions, to run your actions manually in OpenWhisk, and to get their logs.
Here is an example with the action "wand_blur" from the [repository of example actions for FaaSLoad](https://gitlab.com/faasload/actions).

```shell
# list actions
wsk --insecure action list
# activate action
# Actions to be used with FaaSLoad require special parameters related to Swift storage: object is the input filename,
# incont is the input container, and outcont is the output container.
# Parameters related to connecting to Swift storage, and usually defined in "swift_parameter.json", can also be
# overridden here
wsk --insecure action \
  invoke --result dataset_gen/wand_blur \
  --param sigma 1.3424023855536071 --param object 1.jpg --param incont image --param outcont user-wand_blur-out
```

A typical cause of silent failure was that the configuration about connecting to the Swift storage container was wrong:
the action would timeout without any logs.

A difficulty in the context of FaaSLoad in injector mode, is to test actions loaded into OpenWhisk under different user namespaces.
You can use the wsk CLI tool under different users with a command like the following:

```shell
# --auth specifies an authentication token, which in this case is read by cat from the directory of injection traces
wsk action --auth $(cat ../injection/users/user-wand_blur) \
  invoke --result dataset_gen/wand_blur \
  --param sigma 1.3424023855536071 --param object 1.jpg --param incont image --param outcont user-wand_blur-out
```
