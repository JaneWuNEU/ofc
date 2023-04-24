# Apache OpenWhisk: local deployment using Ansible for FaaSLoad

To easily test changes to Apache OpenWhisk's code, it is much easier to create a local installation using Ansible and based on simple Docker containers.
The guide below is based of ["Setting up OpenWhisk on Ubuntu server(s)"](https://github.com/apache/openwhisk/tree/master/tools/ubuntu-setup) to install OpenWhisk on a single Ubuntu server, followed by and merged with ["Deploying OpenWhisk using Ansible"](https://github.com/apache/openwhisk/tree/master/ansible) to install using Ansible.
Ansible will be useful to fetch the logs and hot-swap OpenWhisk's components.

In the context of FaaSLoad, this installation method is useful for setting up FaaSLoad with OpenWhisk, but is also required for the Docker monitor feature (see "Configuration" in [injector.md](injector.md) or in [generator.md](generator.md) for more information about enabling the Docker monitor).

In addition, a practical usage guide for development on OpenWhisk is at the end of this document, under the section "Usage".

## Installation: pre-requisites

The first step is to fetch OpenWhisk's code using git from GitHub:

```shell
git clone https://github.com/apache/openwhisk.git openwhisk
```

Then, there is an easy script for Ubuntu (working on 18.04) to install all dependencies.
Otherwise, install them manually -- see next section.

### Ubuntu 18.04

OpenWhisk's code includes a script to install all the requirements to install on Ubuntu.
In particular, it installs OpenJDK 8, which is required to use the included gradlew script further below.

```shell
cd openwhisk
# Install all required software
tools/ubuntu-setup/all.sh
```

We will use the auto-generated configuration for an ephemeral CouchDB data store, so skip the part about "selecting a data store".
Despite being ephemeral, Docker will keep it "persistent" through reboots of your host machine, but don't rely on it.

Re-log into your user so your addition to the group `docker` is effective (otherwise Gradle cannot access Docker's socket).

### Others (Arch Linux, etc.)

It's all Python-based (working with Python 3.8) so several Python modules are required.
Install them using your package manager or using `sudo pip` (i.e. globally) according to your preference.
Here are the names as listed in PyPI:

 * ansible
 * jinja2
 * docker

In addition, you need the **OpenBSD variant** of `nc` (netcat) command for Ansible playbooks to test for working deployment of the components.
Install it with your package manager (it is most often already installed by your distribution, unless you have
something like Arch Linux).
The OpenBSD variant is required because it uses the `-U` flag to plug into UNIX sockets.

Moreover, for the `postdeploy.yml`, you need `npm` and `zip`.

## Installation

### Install OpenWhisk

First, you might want to keep the log and configuration files through reboots: export the variable `OPENWHISK_TMP_DIR`,
for instance pointing to a directory in "ansible", to make logs and configuration persistent.

Now, generate configuration for OpenWhisk's components:

```shell
# Every Ansible command has to be run from the directory "ansible" because it contains the configuration file for
# Ansible, as well as the playbooks.
cd ansible
ansible-playbook setup.yml
```

In particular, this generates the configuration for the ephemeral CouchDB data store.

Now, compile Apache OpenWhisk and build Docker container images for its components:

```shell
# Go back to OpenWhisk's root directory
cd ..
./gradlew distDocker
# or if you need to change the JRE:
# JAVA_HOME=/usr/lib/jvm/java-8-openjdk/jre ./gradlew distDocker
# or any other JVM, but it needs Java 8
```

If you have errors with Gradle not being able to access Docker's socket, this is because you forgot to re-log into your user to update its groups.
Now Gradle has its daemon running, with the non-updated groups, so stop the daemon with `./gradlew --stop` and
try again.

If you ever need to run a Gradle task again, use this script instead of your local Gradle installation:
it uses the correct version of Gradle (for instance the version available to Ubuntu 18.04 is too old).
In addition, it requires Java 8, so make sure to set your environment to use this version:
either change it globally, or pass `JAVA_HOME=/usr/lib/jvm/<JAVAVERSION>` before invoking the script.

It will take a long time for the first compilation, because it will spawn a Gradle daemon, and then it will pull many Docker containers just for the build.

Now you can execute all the Ansible playbooks to run OpenWhisk's components:

```shell
cd ansible
# create a CouchDB container
ansible-playbook couchdb.yml
# init the DB for OpenWhisk; this is required after every teardown
ansible-playbook initdb.yml
# only do the wipe on fresh deployments because, as the name implies, that wipes the DB so actions, etc. are lost
ansible-playbook wipe.yml
# deploy OpenWhisk components (Kafka queue, controller, etc.)
ansible-playbook openwhisk.yml
# if you want to skip pulling Docker images of the runtimes, for instance to use your own local images, use:
# ansible-playbook openwhisk.yml -e skip_pull_runtimes=true

# install a catalog of public packages and actions
ansible-playbook postdeploy.yml

# run those two to use the API gateway
ansible-playbook apigateway.yml
ansible-playbook routemgmt.yml
```

Please refer to ["Deploying OpenWhisk using Ansible"](https://github.com/apache/openwhisk/tree/master/ansible) to understand which playbooks you might need to run again in the future (on system reboot for instance).
In particular, `wipe.yml` will **erase all actions, etc.**;
you only need to run `openwhisk.yml` to deploy OpenWhisk's components (provided that you already have your CouchDB instance running).
There are also playbooks for individual components such as "invoker.yml" or "controller.yml" to redeploy only one component.

### Install OpenWhisk CLI `wsk` (optional)

As we are installing a development environment, you may want to get the CLI from source, so you can make changes to it.
It is called the "local" mode by the upstream guide.
In the context of FaaSLoad, this is optional, and you will already have a CLI binary "wsk" in the folder "openwhisk/bin", so you can skip to the next section "Setup OpenWhisk CLI".

Fetch the code and compile the CLI:

```shell
# Put the repo at the same level as your openwhisk repo, e.g. in your home
cd ~
git clone https://github.com/apache/openwhisk-cli.git
cd openwhisk-cli
# -PnativeBuild is used to avoid compiling for all platforms
./gradlew releaseBinaries -PnativeBuild
```

Then, come back to OpenWhisk's repo and install the CLI in it:

```shell
cd ~/openwhisk/ansible
ansible-playbook edge.yml -e mode=clean
ansible-playbook edge.yml -e cli_installation_mode=local -e openwhisk_cli_home="~/openwhisk-cli"
```

Now you have your `wsk` CLI version in the "bin" folder of OpenWhisk (so call it with `bin/wsk`).

### Setup OpenWhisk CLI

Follow the guide ["OpenWhisk CLI"](https://github.com/apache/openwhisk/blob/master/docs/cli.md) to set up the CLI;
for convenience, configure it for the guest account automatically created by Ansible playbooks.
FaaSLoad does not use the CLI during normal operations, although you will use it to set up OpenWhisk;
see "OpenWhisk setup" in [injector.md](injector.md) or in [generator.md](generator.md) for more information.
Please note that in this local Ansible setup, you will always have to use the `-i/--insecure` flag because the self-signed certificate to the REST API server is invalid;
this is reflected in FaaSLoad's configuration in "loader.yml", under `openwhisk:disablecert`.

## Usage

The guide ["Deploying OpenWhisk using Ansible"](https://github.com/apache/openwhisk/tree/master/ansible) details a few use cases, I rewrote some of them here.
Hot-swapping a component is used during FaaSLoad setup but is recalled in [injector.md](injector.md) and in [generator.md](generator.md) when needed, so in the context of FaaSLoad, you don't need to read any further.

### Hot-swapping a single component

So indeed the purpose of this installation is to make changes to OpenWhisk, i.e. modifying its components and testing them.
I understand that components are roughly listed by the files in the folder "ansible", such as "invoker", "controller", etc.

Let's say you made changes to code related to the controller (either to the controller's code or to common code used by it), so you want to update it.
You have to rebuild its Docker image and use Ansible to replace the container:

```shell
# Note the parameter dockerImageTag
./gradlew :core:controller:distDocker -PdockerImageTag=myTag
cd ansible
# Note the environment parameter docker_image_tag
ansible-playbook controller.yml -e docker_image_tag=myTag
```

You can omit all Docker image tag parameters if you want to use the `latest` tag.

### Getting the logs

Especially for log-based debugging, you will need to see the logs and outputs of OpenWhisk's components.
`docker logs <container>` shows nothing, because the logs are directly stored where you told Ansible to do so (see above with the environment variable `OPENWHISK_TMP_DIR`).
You can extract them for all components at once with Ansible (requires `rsync`):

```shell
cd ansible
# Do not dump logs from DB (it dumps entities like actions, etc.) nor tests results
ansible-playbook logs.yml -e exclude_logs_from=db,tests
```

This playbook dumps all the logs in a "logs" folder in OpenWhisk's directory.
Logs are under subdirectories named after a component's name and replica number (which is also the Docker container's name of the deployed component);
don't be confused by the empty logs with the component name.
For example, for me, the playbook created an empty log file for the controller, but also a folder named "controller0" that contains the logs for the Docker container of the controller.

### Use local Docker images of action runtimes

You can customize the names and tags of the Docker images that are run as action runtimes (e.g. the NodeJS environment, of the Python environment, etc.) by changing values in "ansible/files/runtimes.json" (the JSON is pretty self-explicit).

Then, redeploy OpenWhisk bu running:

```shell
cd ansible

ansible-playbook setup.yml
ansible-playbook couchdb.yml
ansible-playbook initdb.yml
ansible-playbook wipe.yml
# Note the environment parameter skip_pull_runtimes
ansible-playbook openwhisk.yml -e skip_pull_runtimes=true
```

It is important to prevent the tasks in "openwhisk.yml" from pulling the images if they are only available locally, i.e. you did not push them to Docker Hub.
