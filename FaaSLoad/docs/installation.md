# Install FaaSLoad

This page gives instructions about installing FaaSLoad, whatever the intended mode of use (injector or generator).
After installation, refer to [injector.md](injector.md) or to [generator.md](generator.md) for instructions specific to your usage.

## Dependencies

FaaSLoad is coded in Python, and is installed manually using [pipenv](https://pipenv.pypa.io/en/latest/), so you need them both installed.
pipenv will pull dependencies from PyPI and create a virtualenv to run FaaSLoad from.

In addition, FaaSLoad requires [PyWhisk](https://gitlab.com/Thrar/pywhisk) to interface with OpenWhisk.
If you want to use the monitor, it also requires [PyCGroup](https://gitlab.com/Thrar/pycgroup) to monitor Docker containers.
The installation instructions below will tell you how to install both;
they are not published on PyPI so they will not be installed by pipenv.

Of course, you need OpenWhisk, which is installed below.

## Apache OpenWhisk

First, you need a working OpenWhisk Ansible-based installation.
In order to use the monitor component (i.e., to store memory and CPU usage of functions), a few modifications have been implemented in OpenWhisk, so fetch our [modified OpenWhisk's code](https://gitlab.com/slimfaas/openwhisk):

```shell
git clone https://gitlab.com/faasload/openwhisk.git
```

Then, follow this guide: ["Apache OpenWhisk: local deployment using Ansible for FaaSLoad"](openwhisk_ansible.md).
Do not forget to configure the `wsk` CLI because the generator reads its OpenWhisk configuration from the same file as the CLI, in "~/.wskprops".
Also, do not hesitate to test OpenWhisk's installation by running an sample action, or anything else not related to FaaSLoad.

## FaaSLoad

Leave the "openwhisk" directory, clone FaaSLoad's repository and install using pipenv:

```shell
git clone https://gitlab.com/faasload/faasload.git
cd faasload
# Install with pipenv, it also creates a new virtualenv to do so
# Flag --editable/-e is important, to make pipenv use setup.py and install dependencies from it
pipenv install --editable . 
```

Note the path of the created virtualenv, you will need to write it in the systemd units if you want to use them.
To retrieve the path of the virtualenv afterwards, use `pipenv --venv`.

As stated above, the project also requires dependencies, PyWhisk and PyCGroup.
They can be installed in the virtualenv with the following commands:

```shell
# Go back to the level of FaaSLoad's folder
cd ..
# Clone dependencies
git clone https://gitlab.com/Thrar/pywhisk.git
git clone https://gitlab.com/Thrar/pycgroup.git
# Go back to the installation folder to plug into the virtualenv
cd faasload
pipenv install ../pywhisk
pipenv install ../PyCGroup
```

Then, copy the "config" folder in your "~/.config" folder, renaming it "faasload":

```shell
cp -r config ~/.config/faasload
```

FaaSLoad's loader component will not start without its configuration file "loader.yml";
similarly, the monitor component will not start without its configuration file "monitor.yml".

Every setting is documented inside the configuration files.
You can leave most settings to their default values, however you must set `openwhisk:kafkahost` to the address and port (e.g. `"172.17.0.3:9093"`) of OpenWhisk's Kafka Docker container.
Also check the path to OpenWhisk's installation folder under `openwhisk:home`;
it should point to the directory containing the file "whisk.properties".

See [injector.md](injector.md) or [generator.md](generator.md) for settings specific to each usage mode.

To use the systemd units of the loader and the monitor, fix the paths in the ".service" files by writing the path to the virtualenv where you installed everything (see the comments in the service unit files).
Then, copy the service unit files to the systemd user folder:

```shell
cp *.service ~/.config/systemd/user
```

Finally, if you intend to use the monitor, create the directory where the monitor will put its sockets (see "Configuration" in [injector.md](injector.md) or in [generator.md](generator.md) for more information about enabling the Docker monitor):

```shell
# When installing OpenWhisk, the Ansible playbook tried to mount the non existing sockets in the container, creating the
# directory "/run/wdm" in the process.
# So you have to clean it first (because it created directories with the names of the sockets it tried to mount).
sudo rm -rf /run/wdm/*
# Give ownership to your user, or any user:group relevant to your setup, taking into account that you will run the
# monitor as a normal user with systemctl --user
sudo chown $USER /run/wdm
```

## Database

FaaSLoad will store run dataset in a database.
It is coded to connect to a MySQL (MariaDB) database server on the local host.
Database name, and user name and password can be configured in "loader.yml".
You just need **to create the database** (default name `faasload`) and the user (default name `faasload`, no password).
