# Workload injection traces

This document describes the format of workload injection traces expected by FaaSLoad in injector mode.
It also gives tips on how to set up OpenWhisk with relation to the traces.

## Trace format

### Trace filenames

FaaSLoad's workload injector reads all files from the directory given in its configuration (in "loader.yml", `injection:tracedir`) as trace files.
One file represents:

 * a USER
 * running an ACTION
 * under an amount of MEMORY (in MB)
 * running for a DURATION (in min)
 * and with an average inter-arrival time (AVRGIAT, in min)

This information is represented in the trace's filename like so:

```
USER-ACTION-MEMORY-DURATION-AVRGIAT
```

For example, the trace filename `user004-wand_blur-3072-120-4` describes the workload for the user `user004`'s action `wand_blur`, running with 3072MB (3GB) for 120min (2h) and with an average IAT of 4min.

FaaSLoad expects to find the user and action names in this format, in a trace filename;
other information is only metadata which is not actually required, although it is advised to keep this format.
In particular, the memory allocation is defined when loading the action in OpenWhisk, under the user's namespace, so FaaSLoad has no control over it.

### Trace content

In the trace file, each line is an activation of the action.
A line follows this format (whitespaces are tabs, FaaSLoad will split lines on a tab `\t` character):

```
WAIT    INPUT   PARAM1:VALUE1   PARAM2:VALUE2   ...
```

 * WAIT is the time to wait (in seconds, can be fractional) between the last invocation, and the invocation of the current line
 * INPUT is the complete filename of the input (it will be passed as-is to the action when activated, so make it match with your storage!)
 * PARAMN:VALUEN is the list of parameters for the activation (there is a colon `:` between PARAMN AND VALUEN):
   * PARAMN is the Nth parameter's name as expected by the action
   * VALUEN is the Nth parameter's value

For example, given this trace file, named `user004-wand_blur-3072-120-4`:

```
284	user004/19.jpg	sigma:39.64642930244718
364	user004/496.jpg	sigma:60.88444071760475
```

FaaSLoad will first wait 284s before activating `wand_blur` (i.e., at time 284s) with user `user004`, with the input named `user004/19.jpg` and the parameter `sigma` set to `39.64642930244718`.
Then, it will wait 364s before activating the action again (i.e., at time 284+364=648s), with the input `user004/496.jpg` and `sigma` set to `60.88444071760475`.

## OpenWhisk setup

The traces include references to OpenWhisk users and actions, which you must create manually.

An OpenWhisk user can be created using wskadmin, an executable in "openwhisk/bin", like so:

```shell
openwhisk/bin/wskadmin user create USER > faasload/injector_users/USER
```

With this command, you can create the user USER, and write in the file "faasload/injector_users/USER" its authentication token.
The token is read by FaaSLoad when activation the user's actions.
Set the configuration setting `openwhisk:authkeys` in "loader.yml" to the directory "faasload/injector_users" to tell FaaSLoad where to read the authentication tokens from.

As for the actions, you must load them into OpenWhisk, either by calling `wsk` repeatedly or by using [a Manifest file for `wskdeploy`](https://github.com/apache/openwhisk-wskdeploy) to deploy several actions at once under a package.
Remark that the action name in the trace filename does not include a package name:
FaaSLoad will use this name to find the action information in its database (see "Injection traces" in ["Workload injector mode"](injector.md)), which includes the actual package name.
In other words, you can deploy your actions in a package, under a user namespace.
