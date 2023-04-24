# FaaSLoad: Function-as-a-Service workload injector

The project's goal is to inject a workload to the Function-as-a-Service (FaaS) platform [Apache OpenWhisk](https://openwhisk.apache.org/).

## Installation and usage

This project has two usage modes:

 1. as a **workload injector**: run traces describing serverless functions invocations of many users in OpenWhisk, and monitor their execution time, and more;
 2. as a **dataset generator**: run serverless functions in OpenWhisk and monitor their execution, generating a dataset of memory usage, execution time, and more.

The injector mode can be used to evaluate the FaaS platform OpenWhisk, by observing its behavior under different workloads.
The generator mode can be used to produce a dataset of function invocations that you can feed to a machine learning model for training.

Refer to ["Install FaaSLoad"](docs/installation.md) to install the software, and then refer to the documentation of the ["Injector mode"](docs/injector.md) or to the documentation of the ["Generator mode"](docs/generator.md) for instructions about setup, configuration, usage and data analysis of the two modes.

The sections below give general information about the project's architecture and usage.

## General overview

There are two components; they are not linked to the two usage modes, and are used in both modes:

 1. the **loader**: invoke functions in OpenWhisk, and get information about their executions from OpenWhisk and from the monitor (the other component);
 2. the **monitor**: collect supplementary data about functions' executions, which is retrieved by the loader.

The main component is the loader, and it is used both to inject a workload into OpenWhisk and to generate a dataset of function executions.

The two components are implemented as Python modules, which can be `import`ed, or executed from a terminal with `python -m`.
However, the preferred method is to run them as [systemd service units](https://www.freedesktop.org/wiki/Software/systemd/), to benefit from systemd's execution management and monitoring. 
They are configurable through YAML config files from the "config" folder.

Moreover, in the dataset generator mode, FaaSLoad includes a checkpointing feature: when interrupted (SIGINT and SIGTERM) or after finishing its job, it stores its internal state (including random state).
It is then possible to restart the generation from where it stopped.
See "Checkpointing" in ["Dataset generator mode"](docs/generator.md) for more information.

## Ties to OpenWhisk

We [deploy OpenWhisk locally using Ansible](https://github.com/apache/openwhisk/tree/master/ansible), in order to interface with it, and to monitor the executions of functions.
The loader interacts with OpenWhisk via its [REST API](https://github.com/apache/openwhisk/blob/master/docs/rest_api.md);
it invokes functions and retrieve execution information this way.
The monitor interacts with OpenWhisk via a UNIX socket, inserted into one of OpenWhisk's components that is modified for this purpose.
To monitor memory and CPU usage, it uses [Linux' cgroups](https://www.man7.org/linux/man-pages/man7/cgroups.7.html), which is in fact how containers, used by OpenWhisk to execute functions, are implemented by Docker.

To summarize, the loader component of FaaSLoad can be easily detached from OpenWhisk and reused on another FaaS platform;
and the monitor component is mostly generic but requires low level information about the FaaS platform's Docker container usage, which would need to be specifically adapted to another platform.
