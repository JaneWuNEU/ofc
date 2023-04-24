# FaaSLoad actions

This document describes how OpenWhisk actions should be written for usage with FaaSLoad.
It covers the following items:

 * access to storage
 * common parameters
 * return values

## Access to storage

Example actions written for FaaSLoad were designed for the OpenStack object store [Swift](https://www.openstack.org/software/releases/victoria/components/swift).
In Swift, objects are accessed with their filenames, and a stored in containers.
This is reflected in FaaSLoad sending container names and input filenames to activated actions (see "Common parameters" below).

Example actions find the Swift configuration (authentication URL, user and key) in their default parameters stored in OpenWhisk.
They read from and write to storage themselves (using a Swift client library for the language they are written in), without any action from FaaSLoad.
Thus, **FaaSLoad is not tied to a specific storage**, and container and file names can be repurposed for your storage of choice.

## Common parameters

Actions written for OpenWhisk should expect to receive a dictionary mapping parameter names to values.
Of course, your actions may expect any parameter specific to them, but FaaSLoad will always give them the following parameters:

 * `incont`: storage container (this is Swift jargon, see "Access to storage" above) where the `object` input is stored; its value is the name of the user under which the action is activated
 * `object`: filename of the input, as found under the container `incont`
 * `outcont`: storage container where the action's output should be stored; actions determine the output object filename themselves

As you can see, the storage configuration is not passed by FaaSLoad.
You are expected to set it as default parameters in the action declarations in OpenWhisk.

## Return values

OpenWhisk actions return dictionaries with custom fields.
FaaSLoad expects to find a few fields in it (you can add your own), that are stored in its database:

 * `outputsize`: size in bytes of the output of the function as written to storage
 * `start_ms`: date (as a timestamp, in milliseconds) of the start of the action, taken from inside the action
 * `times`: a dictionary with the following duration fields (in milliseconds, see below):
   * `extract`: duration of the extract phase (downloading input from storage)
   * `transform`: duration of the transform phase (processing the input)
   * `load`: duration of the load phase (uploading output to storage)

Cloud functions (e.g. actions in OpenWhisk) are most often designed as Extract-Transform-Load (ETL) processes.
FaaSLoad expects the actions to time those phases by themselves, and to return the durations in the result dictionary, to be stored in its database.
