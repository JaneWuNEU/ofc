# Fake workload traces for generator mode

FaaSLoad's dataset generator mode is very close to the workload injector mode.
It simply builds fake workload traces in order to run every action declared in its database, on the number of inputs set in its configuration.

Because traces are built automatically by FaaSLoad, a bit of setup must be done predictably.

## Actions and users

The base to build the fake workload traces is the table `functions` in FaaSLoad's database, which you fill as instructed in "Setup" in ["Dataset generator mode"](generator.md).
Also, FaaSLoad activates actions via users with predictable names of the form "user-ACTION", which you can create by following the instructions in the same document as for the actions.

## Inputs

In generator mode, FaaSLoad builds input data filenames of the form `INPUT_ID.INPUT_EXT`.
For example, an image processing function will receive as the parameter "object" the filename "1.jpg" for the first activation, then on the next activation the filename "2.jpg", etc.
So you have to load your inputs in your storage accordingly.

_You can customize the extensions by modifying the dict `INPUT_EXTENSIONS` in `loader.generator`._

## Function-specific parameters

When building the fake traces, FaaSLoad must produce random but valid values for an action's parameters.
To do so, parameters are described in the `parameters` field of the table `functions` in FaaSLoad's database.
This field is expected to be a YAML string containing a list of dictionaries.
Each dictionary describes one parameter.
As a special case, the parameter "object" may be included in this list, and will simply be ignored by FaaSLoad (because this is the input object filename, see above).

Any parameter dictionary must include the following fields (other fields are ignored):

 * `name`: name of the parameter
 * `type`: type of the parameter; any value of `range_int`, `range_float` or `ensemble` (see below)

Depending on the `type`, other fields are expected:

 * `range_int` and `range_float`: fields `min` and `max` (integers or floats) to specify the range of valid values (included)
 * `ensemble`: field `value`, the list of valid values to chose from

See below an example:

```yaml
- name: sigma
  type: range_float
  description: sigma blurring coefficient
  min: 0.3
  max: 100
- name: width
  type: range_int
  description: target width
  min: 100
  max: 1920
- name: format
  type: ensemble
  description: target format
  values: [webp, tiff, png]
```

Thus, parameter values are produced randomly (uniform distributions).
The random number generator (RNG) is initialized with the seed specified in "loader.yml" under `generation:seed`.
If FaaSLoad in generator mode is interrupted, the RNG state is restored.
