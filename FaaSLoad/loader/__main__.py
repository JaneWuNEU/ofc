"""Entrypoint to run the dataset generator.

The `main` method handles:

 1. preparing configuration for OpenWhisk user and administration APIs, and database access
 2. loading checkpointed generator state, and writing it
 3. running the generator

## Configuration

OpenWhisk user API configuration is read from the default place at "~/.wskprops", as set by OpenWhisk when configuring
its CLI.

Other configuration is taken from the defaults of this module (see "__init__.py") and completed by reading the
configuration file.

## State checkpointing

The method `generator.generate` handles action invocation errors to continue generating, and catches other, unexpected
errors before returning its current state. It also catches SIGINT and SIGTERM to allow for saving the checkpoint upon
user interruption with Ctrl-C and receiving termination signal from systemd when run as a service.

Before running the generator, the `main` method here tries to load a checkpointed state:

 * from the file given as the first argument on the command line if present
 * from a "*.genstate" file in $HOME if found

When loading from a file from $HOME, it loads the state from the latest file, as determined by the date written in ISO
format in the file's name.

The method `generator.generate` is the one actually responsible for continuing generation from the checkpoint, including
restoration of its RNG and cleaning any corrupted data in the database. About the latest point, there is a security in
place that will prevent deletion from the database of too many records when recovering, to prevent data loss due to
loading the wrong state.
"""

import logging
import logging.config
import os
import pickle
import sys
from datetime import datetime
from glob import glob
from pickle import PickleError

from pywhisk.client import AdministrationConfiguration, read_api_cfg as read_wsk_cfg

from utils import try_read_configuration
from . import DEFAULTS, OpenWhiskConfiguration
from .database import FaaSLoadDatabase
from .generation import build_traces as build_generator_traces, GenerationException
from .injection import inject, InjectorExitStates, load_trace as load_injection_trace, TraceParsingException


class StateLoaderError(Exception):
    """An error happened while loading a checkpointed generator state."""

    def __init__(self, msg, filename=None):
        super().__init__(msg)

        self.filename = filename


def _read_auth_keys(auth_dir):
    auth = {}
    for filepath in glob(os.path.join(auth_dir, '*')):
        with open(filepath, 'r') as auth_file:
            auth[os.path.basename(filepath)] = tuple(auth_file.read().rstrip().split(':', maxsplit=1))

    return auth


def main():
    """Main method to run the generator from CLI."""
    import urllib3

    conf = try_read_configuration(os.path.expanduser('~/.config/faasload/loader.yml'), DEFAULTS)

    logger = logging.getLogger('main')

    gen_cfg = conf['generation']._replace(
        statedir=os.path.expanduser(os.path.expandvars(conf['generation'].statedir)))
    logger.debug('dataset generator configuration: %s', gen_cfg)

    docker_mon_cfg = conf['dockermonitor']._replace(
        measurementsock=os.path.expanduser(os.path.expandvars(conf['dockermonitor'].measurementsock)))
    logger.debug('monitor access configuration: %s', docker_mon_cfg)

    db_cfg = conf['database']
    logger.debug('database configuration: %s', db_cfg)

    # disable certificate checking because the self-signed certificate of local Ansible deployments is broken
    wsk_cfg = OpenWhiskConfiguration(kafkahost=conf['openwhisk'].kafkahost,
                                     **read_wsk_cfg(cert=not conf['openwhisk'].disablecert)._asdict())
    # and disable associated warning
    urllib3.disable_warnings()
    # read additional authorization keys if specified
    if conf['openwhisk'].authkeys:
        wsk_cfg.auth.update(_read_auth_keys(os.path.expanduser(os.path.expandvars(conf['openwhisk'].authkeys))))
    logger.debug('OpenWhisk API configuration: %s', wsk_cfg)

    logger.warning('certificate verification of OpenWhisk API gateway is disabled because the certificate of the local '
                   'Ansible deployment is broken')
    wsk_admin_cfg = AdministrationConfiguration(os.path.expanduser(os.path.expandvars(conf['openwhisk'].home)))

    inj_cfg = conf['injection']._replace(
        tracedir=os.path.expanduser(os.path.expandvars(conf['injection'].tracedir)))
    logger.debug('trace injector configuration: %s', inj_cfg)

    db = FaaSLoadDatabase(db_cfg)

    if gen_cfg.enabled:
        state = None

        try:
            # try to get the genstate file with the youngest date in its name from the configured directory
            most_recent = max((fn for fn in glob(os.path.join(gen_cfg.statedir, '*.genstate'))),
                              key=lambda fn: datetime.fromisoformat(os.path.splitext(os.path.basename(fn))[0]))
        except ValueError:
            # max()'s arg is an empty sequence: no state loading
            logger.info('no state given to load and no state file found in "%s": fresh start', gen_cfg.statedir)
        else:
            try:
                with open(most_recent, 'rb') as state_file:
                    # list of tuples (run_id, rng_state)
                    state = pickle.load(state_file)

                logger.info('loaded most recent state from "%s"', gen_cfg)
            except (OSError, EOFError, PickleError):
                logger.exception('found state file at "%s" but failed loading state: aborting', most_recent)
                db.close()
                sys.exit(1)

        try:
            traces = build_generator_traces(db, gen_cfg, state=state)
        except GenerationException:
            logger.exception('failed generating injection traces')
            db.close()
            sys.exit(1)

        if state:
            # for each injector, delete runs with ID greater than the last good ID
            # this does not delete runs for which the ActivationMonitor failed fetching data, they will remain with
            # NULL values
            db.delete_lost_runs(state)
            logger.debug('wiped lost runs after loading state')

        logger.info('generated %d injection traces', len(traces))
    else:
        traces = []
        for trace_filepath in glob(os.path.join(inj_cfg.tracedir, '*')):
            try:
                logger.debug('reading trace file "%s"', trace_filepath)
                traces.append(load_injection_trace(inj_cfg.tracedir, db_cfg))
            except TraceParsingException:
                logger.exception('failed loading trace file "%s": aborting', trace_filepath)
                db.close()
                sys.exit(1)

        db.wipe()
        logger.debug('wiped database')

        logger.info('read %d injection traces from "%s"', len(traces), inj_cfg.tracedir)

    db.close()

    injectors = inject(traces, db_cfg=db_cfg, inj_cfg=inj_cfg, wsk_cfg=wsk_cfg, wsk_admin_cfg=wsk_admin_cfg,
                       docker_mon_cfg=docker_mon_cfg)

    nb_success = 0
    nb_interrupted = 0
    nb_failure = 0
    nb_stillrunning = 0
    for injector in injectors:
        inj_state = injector.get_state()

        if inj_state.exit is InjectorExitStates.EndOfTrace:
            nb_success += 1
            logger.info('injector %s ended successfully after %d runs', injector.name, inj_state.last_run)
        elif inj_state.exit is InjectorExitStates.Interrupted:
            nb_interrupted += 1
            logger.warning('injector %s was interrupted after %d runs', injector.name, inj_state.last_run)
        elif inj_state.exit is InjectorExitStates.Error:
            nb_failure += 1
            logger.error('injector %s ended in error after %d runs', injector.name, inj_state.last_run)
        else:
            nb_stillrunning += 1
            logger.critical('injection ended with injector %s still running', injector.name)

    if nb_stillrunning == 0:
        logger.info(
            'injection ended with %d successful, %d interrupted, and %d failed injectors, out of %d total injectors',
            nb_success, nb_interrupted, nb_failure, len(injectors))
    else:
        logger.info(
            'injection ended with %d successful, %d interrupted, and %d failed injectors, out of %d total injectors '
            '(%d still running)', nb_success, nb_interrupted, nb_failure, len(injectors), nb_stillrunning)

    if gen_cfg.enabled:
        state = [injector.get_state() for injector in injectors]
        state_filepath = os.path.join(gen_cfg.statedir,
                                      datetime.now().isoformat(sep='_', timespec='seconds') + '.genstate')
        try:
            with open(state_filepath, 'wb') as state_file:
                pickle.dump(state, state_file)
            logger.info('wrote state to "%s"', state_filepath)
        except OSError:
            logger.critical('FAILED SAVING GENERATOR STATE TO "%s": DUMPING STATE TO CONSOLE', state_filepath,
                            exc_info=True)
            print(repr(state))


if __name__ == '__main__':
    main()
