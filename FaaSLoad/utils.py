import logging.config
import sys

import yaml


def try_read_configuration(config_filepath, defaults):
    try:
        with open(config_filepath, 'r') as config_file:
            conf = yaml.full_load(config_file)
    except (OSError, yaml.YAMLError):
        logging.exception('failed reading configuration from "%s": aborting', config_filepath)
        sys.exit(1)
    else:
        logging.config.dictConfig(conf['logging'])
        del conf['logging']
        # Convert dicts to my namedtuples, replacing null values with defaults.
        # This goes only one level deep in replacing null values in dicts.
        conf = {section_name: defaults[section_name]._replace(**{
            confkey: ({subconfkey: (
                subconfval if subconfval is not None else getattr(defaults[section_name], confkey)[subconfkey])
                          for subconfkey, subconfval in confval.items()}
                      if isinstance(confval, dict) else confval)
            for confkey, confval in section.items() if confval is not None})
                for section_name, section in conf.items()}

        return conf
