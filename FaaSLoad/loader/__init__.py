"""Inject load traces into Apache OpenWhisk

This module is executable:

    python -m faasload

Content:
 * `database`: facilities related to interacting with the database for the dataset
 * `functions`: facilities related to loading the actions used to generate the dataset into the database
 * `generator`: facilities related to producing traces used by the injector to generate a dataset of action invocations
 * `injection`: the load injector
 * `inputs`: facilities related to loading action inputs into the database
"""

from collections import namedtuple

GenerationConfiguration = namedtuple('GenerationConfiguration',
                                     ['enabled', 'seed', 'statedir', 'interinvocationtime', 'nbinputs'])
DatabaseConfiguration = namedtuple('DatabaseConfiguration', ['user', 'password', 'database'])
# OpenWhiskConfiguration is used to store both the configuration read from our configuration file, and the configuration
# read by PyWhisk, which fills the fields "host", "auth" and "cert" for which default values are defined
OpenWhiskConfigurationFromFile = namedtuple('OpenWhiskConfigurationFromFile',
                                            ['home', 'disablecert', 'authkeys', 'kafkahost'])
OpenWhiskConfiguration = namedtuple('OpenWhiskConfiguration', ['host', 'kafkahost', 'auth', 'cert'])
DockerMonitorConfiguration = namedtuple('DockerMonitorConfiguration', ['enabled', 'measurementsock'])
InjectionConfiguration = namedtuple('InjectionConfiguration', ['tracedir', 'fetchlogs'])

# In this structure, None means that the value is mandatory in the configuration file
DEFAULTS = {
    'generation': GenerationConfiguration(
        enabled=False,
        seed=19940503,
        statedir='~/faasload/states',
        interinvocationtime=60,
        nbinputs=None,
    ),
    'database': DatabaseConfiguration(
        user='faasload',
        password='',
        database='faasload',
    ),
    'openwhisk': OpenWhiskConfigurationFromFile(
        home='~/openwhisk',
        disablecert=True,
        authkeys='',
        kafkahost=None,
    ),
    'dockermonitor': DockerMonitorConfiguration(
        enabled=True,
        measurementsock='/run/wdm/meas',
    ),
    'injection': InjectionConfiguration(
        tracedir='~/faasload/injection-traces',
        fetchlogs={
            'timeout': 5,
            'backofftime': 0.5,
        },
    )
}
