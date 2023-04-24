# SlimFaaS: OpenWhisk actions for dataset generation and evaluation

This repository contains cloud functions ("actions") for Apache OpenWhisk. They are executed to generate a training and
testing dataset for the machine-learning part, and to evaluate the SlimFaaS system.

## Quick start

Assuming you have all the dependencies (see below), there are two steps to use the functions:

 1. build the functions: run `make` in the main folder
 2. load the functions to OpenWhisk: run `make deploy` (assuming you have the executable "wskdeploy" in the parent folder)

The build dependencies are Docker, `zip`, and most importantly a compatible NodeJS version: currently, OpenWhisk's most
up-to-date NodeJS action is version 12, so NodeJS actions have module versions compatible with this version, and **you must
use NodeJS 12 to build them**.

To deploy, you need [`wskdeploy`](https://github.com/apache/openwhisk-wskdeploy/) in the parent folder (i.e. accessible with
`../wskdeploy`,)

## Details

Functions are built in the "build" directory as Zip archives, because they all require dependencies; in addition, a few
functions (such as the ones in "src/py\_wand" which are based on the Python library Wand, of which ImageMagick is a
dependency) require a special Docker runtime image, which is built and added to the local Docker image repository. In
particular, functions extract data from, and load data to a Swift storage backend, and as such, they all have a dependency on
a Swift client library.

Actions are deployed using [`wskdeploy`](https://github.com/apache/openwhisk-wskdeploy/). The deployment is based on the
Manifest file "manifest.yml" so just run `wskdeploy` from this folder (i.e. run `../wskdeploy` from "openwhisk-actions" if you
copied the executable "wskdeploy" in the parent folder). Functions are deployed as actions under the same package (named
"dataset\_gen", this can be configured in the Manifest), and under the default user for the `wsk` command.

The folder "src" contains action runtimes, i.e. each folder corresponds to a general runtime (Python, NodeJS...) and a set of
dependencies (such as Wand for "py\_wand"). Actions under an action runtime folder are based on the same runtime, and can be
built by the same Makefile found in the action runtime folder.

## Actions

In this section I explain what are the specific steps taken to build the different action runtimes (i.e. each subfolder of
"src"), as found in their respective Makefiles. Notes indicate how Makefiles actually slightly differ from what is shown here;
you will find more details in the Makefiles.

In a general manner, there are two steps:

 * build a dependency package: a virtualenv for Python actions, "node\_modules" folders for NodeJS actions;
 * build a runtime image: a customized Docker image embedding more software pieces: native dependencies, build dependencies,
   or the main dependency of a function for various reasons.

All functions have a dependency package, because they all depend on a Swift client library; however they may not need a
runtime image.

### Python Wand

Actions based on the Python 3 library Wand include a virtualenv for the Python module dependency to Wand, and require a custom
Docker image for the actual native dependency to ImageMagick (as Wand is only a ctypes wrapper to ImageMagick). These two
preliminary builds are only required once for all Wand actions.

#### Build the runtime image for Wand actions

Build the Python Wand runtime, that is exactly [OpenWhisk's Python 3
runtime](https://github.com/apache/openwhisk/blob/master/docs/actions-docker.md) but with the added dependency to ImageMagick.

To build the Docker image:

```sh
docker build -t python3action:wand .
```

_Note: the Makefile uses a trick to prevent Docker from sending surrounding files and directories to the daemon._

There is no need to push it to Docker Hub if you don't want to. Contrary to what the guide says, OpenWhisk will happily use
the local image when you use an explicit tag such as `wand` here (`latest` would force a refresh behavior).

Note that due to using a custom Docker image, **the kind of the action is now "blackbox"**.

#### Build the Python virtualenv

Build the virtualenv [using OpenWhisk's Python 3 action
runtime](https://github.com/apache/openwhisk/blob/master/docs/actions-python.md), all Wand actions have the exact same
requirements.

To build the virtualenv:

```sh
docker run --rm -v "$PWD:/tmp" openwhisk/python3action bash \
    -c "cd /tmp && virtualenv virtualenv && source virtualenv/bin/activate && pip install -r requirements.txt"`
```

_Note: the Makefile also fixes ownership of the built directory._

#### Build the action

You can now create the action by fusing the instructions for using a custom Docker image (i.e.\ using the `--docker` flag of
`wsk action create`) and for creating an action from a zip archive:

```sh
# Which Wand action you want to build
ACTION=wand_<action name>

# Creating the archive is a bit convoluted to get the paths right
zip -r $ACTION.zip virtualenv; zip -j $ACTION.zip $ACTION/__main__.py
```

And for manual action creation, if we were not to use `wskdeploy`:
```sh
# we don't need the --kind flag because the runtime is given by the --docker flag
wsk action create $ACTION --docker python3action:magick $ACTION.zip
```

### NodeJS Sharp

Actions based on the NodeJS Sharp library include the "node\_modules" with the dependencies. Otherwise, building them is
simpler than building Python Wand actions (only requiring the dependency package and no custom runtime image). You can create
an action with:

```sh
# Which Sharp action you want to build
ACTION=sharp_<action name>

cd $ACTION
# use `ci` to use exactly the dependencies in package-lock
npm ci
zip -r ../$ACTION.zip *
cd ..
```

And for manual action creation, if we were not to use `wskdeploy`:
```sh
# we need the --kind flag because we use an archive
wsk action create $ACTION --kind nodejs:10 $ACTION.zip
```

Although all actions have the same dependencies and end up with the same "node\_modules" directory, it is done this way
because of NPM, and to keep actions as individual NodeJS packages.

