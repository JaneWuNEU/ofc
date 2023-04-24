import json
import logging
import os
import re
import signal
import socket
import sys
import time
from collections.abc import Iterator
from collections import namedtuple
from datetime import datetime, timedelta
from enum import auto as auto_enum, Enum
from queue import Empty, SimpleQueue
from threading import Event, Thread

import pywhisk.action
import pywhisk.activation
from kafka import KafkaConsumer
from pywhisk.admin.docker import get_docker_id as whisk_get_docker_id
from pywhisk.client import ActionError, OpenWhiskException

from .database import FaaSLoadDatabase, FaaSLoadDatabaseException

InjectionTracePoint = namedtuple('InjectionTracePoint', ['wait', 'params'])
InjectorState = namedtuple('InjectorState', ['exit', 'last_run', 'global_last_run', 'trace_state'])
InjectionTraceState = namedtuple('InjectionTraceState', ['user', 'function'])


class InjectionTrace(Iterator):
    def __init__(self, user, function, points):
        self.user = user
        self.function = function
        self.points = points

    def get_state(self):
        return InjectionTraceState(self.user, self.function)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.points)


TRACEPOINT_MAX_WAIT_ERROR = timedelta(seconds=1)


class InjectorExitStates(Enum):
    Running = auto_enum()
    Interrupted = auto_enum()
    Error = auto_enum()
    EndOfTrace = auto_enum()


class InjectorNotifications(Enum):
    Injected = auto_enum()
    Done = auto_enum()


class ActivationMonitorNotifications(Enum):
    ActivationDataFetched = auto_enum()


def load_trace(trace_filepath, db):
    trace_filename_match = re.match(r'(\w+)-(\w+)-', os.path.basename(trace_filepath))

    if not trace_filename_match:
        raise TraceParsingException('failed parsing trace filename')

    user, func_name = trace_filename_match.group(1), trace_filename_match.group(2)

    func = db.select_function(func_name)

    points = []
    with open(trace_filepath, 'r', newline='') as trace_file:
        for point_id, point in enumerate(line.rstrip().split('\t') for line in trace_file):
            try:
                wait = timedelta(seconds=int(point[0]))
                objectname = os.path.basename(point[1])

                params = {arg: value for arg, value in [tuple(argvalue.split(':')) for argvalue in point[2:]]}
            except (IndexError, TypeError):
                raise TraceParsingException(f'failed parsing trace point #{point_id + 1}')

            params['incont'] = user
            params['object'] = objectname
            # func_name and not func.name, because the latter includes the namespace, which we do not want here
            params['outcont'] = user + '-' + func_name + '-out'

            points.append(InjectionTracePoint(wait=wait, params=params))

    return InjectionTrace(user=user, function=func, points=points)


def inject(traces, db_cfg, inj_cfg, wsk_cfg, wsk_admin_cfg, docker_mon_cfg):
    logger = logging.getLogger('injection')

    act_mon = ActivationMonitor(db_cfg=db_cfg, wsk_cfg=wsk_cfg, wsk_admin_cfg=wsk_admin_cfg,
                                docker_mon_cfg=docker_mon_cfg)
    act_mon.start()

    inj_q = SimpleQueue()

    injectors = []

    for trace in traces:
        injectors.append(Injector(
            trace=trace,
            notif_queue=inj_q,
            cfg=inj_cfg,
            db_cfg=db_cfg,
            wsk_cfg=wsk_cfg,
            wsk_admin_cfg=wsk_admin_cfg,
        ))

    # I try to start all threads as close to each other as possible
    for injector in injectors:
        injector.start()

    logger.info('started %d injectors', len(injectors))

    # sys.exit raises SystemExit, so finally clauses will be executed
    # Python already stores its default SIGINT handler (but not the SIGTERM one, probably because it does not replace it
    # and uses the system's default
    signal.signal(signal.SIGINT, lambda *_: sys.exit(0))
    old_sigterm_handler = signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))

    try:
        _wait_injection(act_mon, inj_q, injectors, logger)

        logger.info('all injectors terminated (possibly in errors, check below)')
    except SystemExit:
        logger.warning('interrupted; terminating injector threads...')

        for injector in injectors:
            injector.terminate()
            injector.join()
    finally:
        signal.signal(signal.SIGINT, signal.default_int_handler)
        signal.signal(signal.SIGTERM, old_sigterm_handler)

        act_mon.terminate()
        act_mon.join()

        return injectors


def _wait_injection(act_mon, inj_q, injectors, logger):
    pending_acts = set()
    while any(injector.exit_state is InjectorExitStates.Running for injector in injectors) or pending_acts:
        # 1. wait for a notification from the ActivationMonitor
        mon_notif = act_mon.notification_queue.get()
        if mon_notif['body']['msg'] != ActivationMonitorNotifications.ActivationDataFetched:
            logger.error('unexpected notification "%s" from activation monitor', mon_notif['body']['msg'])

        # 2. consume potential notifications from injectors
        try:
            while True:
                inj_notif = inj_q.get(block=False)

                if inj_notif['body']['msg'] is InjectorNotifications.Injected:
                    pending_acts.add(inj_notif['body']['activation'])
                elif inj_notif['body']['msg'] is InjectorNotifications.Done:
                    inj_notif['injector'].join()
                    continue
                else:
                    logger.error('unexpected notification "%s" from injector thread %s', inj_notif['body']['msg'],
                                 inj_notif['injector'].name)
        except Empty:
            pass

        # 3. remove activation from pending set
        logger.debug('received ActivationDataFetched notification for activation %s',
                     mon_notif['body']['activation'])
        pending_acts.remove(mon_notif['body']['activation'])


class Injector(Thread):
    def __init__(self, trace, notif_queue, cfg, db_cfg, wsk_cfg, wsk_admin_cfg):
        super().__init__(name=trace.user + '/' + trace.function.name)

        self.trace = trace

        self.notification_queue = notif_queue

        self.db = FaaSLoadDatabase(db_cfg)

        self.cfg = cfg
        self.wsk_cfg = wsk_cfg
        self.wsk_admin_cfg = wsk_admin_cfg

        self.run_id = 0
        self.global_run_id = 0

        self.exit_state = InjectorExitStates.Running

        self.terminate_event = Event()
        self.terminate_event.clear()

        self.logger = logging.getLogger('injector')

    def get_state(self):
        return InjectorState(exit=self.exit_state, last_run=self.run_id, global_last_run=self.global_run_id,
                             trace_state=self.trace.get_state())

    def run(self):
        wait_stop = datetime.now()
        # noinspection PyBroadException
        try:
            for run_id, point in enumerate(self.trace):
                if self.terminate_event.is_set():
                    self.exit_state = InjectorExitStates.Interrupted
                    self.logger.warning('interrupted (last good run: %d)', self.run_id)
                    break

                self.logger.info('run #%d', run_id + 1)

                wait_start = datetime.now()
                compensated_wait = point.wait - (wait_start - wait_stop)
                if compensated_wait <= timedelta(seconds=0):
                    self.logger.warning('invoking previous run delayed invocation by %s', -compensated_wait)
                else:
                    self.logger.debug(
                        'wait before the run: %s (compensated from %s because of the previous invocation)',
                        compensated_wait, point.wait)
                    time.sleep(compensated_wait.total_seconds())
                wait_stop = datetime.now()

                actual_wait = wait_stop - wait_start
                if actual_wait - compensated_wait > TRACEPOINT_MAX_WAIT_ERROR:
                    self.logger.warning('waited %s instead of %s (%s too long, above the maximum wait error of %s)',
                                        actual_wait, compensated_wait, actual_wait - point.wait,
                                        TRACEPOINT_MAX_WAIT_ERROR)
                try:
                    global_run_id, act = self.inject_one(point.params)
                except InjectionException:
                    self.exit_state = InjectorExitStates.Error
                    self.logger.exception('failed injecting trace point #%d: %s', run_id + 1, point)
                    break

                self.run_id = run_id + 1
                self.global_run_id = global_run_id

                self.logger.debug('activated with ID %s for run #%d (global run #%d)', act.activationId, self.run_id,
                                  self.global_run_id)

                self.notification_queue.put({
                    'injector': self,
                    'body': {
                        'msg': InjectorNotifications.Injected,
                        'activation': act.activationId,
                    },
                })
            else:
                self.exit_state = InjectorExitStates.EndOfTrace
                self.logger.info('reached end of injection trace after %d runs', self.run_id)
        except Exception:
            self.exit_state = InjectorExitStates.Error
            self.logger.exception(
                'unexpected error (last good run #%d, global run #%d)', self.run_id, self.global_run_id)
        finally:
            self.db.close()

            self.notification_queue.put({
                'injector': self,
                'body': {
                    'msg': InjectorNotifications.Done,
                }
            })

    def terminate(self):
        self.terminate_event.set()

    def inject_one(self, params):
        """Inject one trace point, i.e. execute the function with given parameters.

        :param params: the parameters of the function invocation, including the function input
        :type params: dict

        :returns: a tuple of the global ID of the run as stored in the database, and the Activation for the run
        """
        if self.logger.isEnabledFor(logging.INFO):
            params_str = ', '.join(f'{name}={value}' for name, value in params.items())
            self.logger.info('invoking %s(%s)', self.trace.function.name, params_str)

        # INVOKE THE ACTION
        try:
            act = pywhisk.action.invoke(self.trace.function.name, self.trace.user, self.wsk_cfg, params, blocking=False)
        except (OpenWhiskException, KeyError) as err:
            raise InjectionException('failed invoking function') from err
        except ActionError as err:
            # If the action failed for a "developer error", we try to get its logs for convenience
            if self.logger.isEnabledFor(logging.WARNING):
                app_logs = _try_get_app_logs(err.activation.activationId, self.wsk_cfg,
                                             int(self.cfg.fetchlogs['timeout'] // self.cfg.fetchlogs['backofftime']),
                                             self.cfg.fetchlogs['backofftime'])
                self.logger.warning('failed invoking function: application error\n' + '\n\t'.join(app_logs))
            act = err.activation

        self.logger.debug('invoked %s under activation %s', self.trace.function.name, act.activationId)

        # store partial run info, to be updated in the future by the ActivationMonitor
        try:
            rec_id = self.db.insert_partial_run({
                'function_id': self.trace.function.id,
                'namespace': self.trace.user,
                'activation_id': act.activationId,
            })
            self.db.insert_parameters(rec_id, params)
        except FaaSLoadDatabaseException as err:
            raise InjectionException('failed storing partial run into the database') from err

        return rec_id, act


def _try_get_app_logs(activation_id, wsk_cfg, max_tries, back_off):
    for _ in range(max_tries):
        try:
            return pywhisk.activation.logs(activation_id, '_', wsk_cfg)
        except OpenWhiskException:
            time.sleep(back_off)

    return [f'logs for activation {activation_id} unavailable']


class ActivationMonitor(Thread):
    # Duration of one polling session
    # After polling for this duration, the monitor checks its termination flag and then resumes polling immediately if
    # it is not set.
    POLL_TIME_MS = 10000

    def __init__(self, db_cfg, wsk_cfg, wsk_admin_cfg, docker_mon_cfg):
        super().__init__(name='ActivationMonitor')

        self.db = FaaSLoadDatabase(db_cfg)
        self.wsk_cfg = wsk_cfg
        self.wsk_admin_cfg = wsk_admin_cfg
        self.docker_mon_cfg = docker_mon_cfg

        self.kafka_cons = KafkaConsumer('events', bootstrap_servers=[self.wsk_cfg.kafkahost],
                                        value_deserializer=json.loads)

        self.run_event = Event()
        self.run_event.set()

        self.notification_queue = SimpleQueue()

        self.logger = logging.getLogger('activationmon')

    def run(self):
        # we need to poll() for new messages in order to periodically check the termination flag
        while self.run_event.is_set():
            msgs = self.kafka_cons.poll(timeout_ms=ActivationMonitor.POLL_TIME_MS)

            if msgs:
                msgs = [cons_rec for topic_part in msgs for cons_rec in msgs[topic_part]]

            for msg in msgs:
                if msg.value['eventType'] != 'Activation':
                    continue

                self.logger.debug('received Kafka activation message: %s', msg)

                # wait a bit for OpenWhisk to store the record in its DB
                time.sleep(0.5)
                self._handle_activation_event(msg)

    def _handle_activation_event(self, msg):
        act_id = msg.value['body']['activationId']
        user_name = msg.value['namespace']

        self.notification_queue.put({
            'body': {
                'msg': ActivationMonitorNotifications.ActivationDataFetched,
                'activation': act_id,
            },
        })

        try:
            act = pywhisk.activation.get(act_id, user_name, self.wsk_cfg)
        except OpenWhiskException as err:
            self.logger.critical('failed fetching activation data for activation %s of user %s', act_id,
                                 user_name)
            self.logger.critical('reason: %s', err)
            return

        try:
            self.db.update_activation(act.activationId, {
                'failed': not act.response.success,
                'start': act.start,
                'end': act.end,
                'wait_time': next((a for a in act.annotations if a['key'] == 'waitTime'), {'value': None})['value'],
                'init_time': next((a for a in act.annotations if a['key'] == 'initTime'), {'value': None})['value'],
                'output_size': act.response.result['outputsize'] if act.response.success else None,
                'extract_time': round(
                    act.response.result['times']['extract']) if act.response.success else None,
                'transform_time': round(
                    act.response.result['times']['transform']) if act.response.success else None,
                'load_time': round(act.response.result['times']['load']) if act.response.success else None,
            })
        except FaaSLoadDatabaseException:
            self.logger.critical('failed storing data of activation %s of user %s into the database',
                                 act.activationId, user_name)
            return

        if self.docker_mon_cfg.enabled and act.response.success:
            try:
                cont_id = whisk_get_docker_id(act.activationId, self.wsk_admin_cfg)
            except ValueError:
                self.logger.critical('failed getting container ID of activation %s of user %s',
                                     act.activationId, user_name)
                return

            try:
                res = self._get_resource_usage(cont_id, act.start, act.end)
            except (ValueError, OSError) as err:
                self.logger.critical('failed fetching resource usage measurements of activation %s of user %s: %s',
                                     act.activationId, user_name, err)
                return

            try:
                self.db.insert_resources(act.activationId, res)
            except FaaSLoadDatabaseException:
                self.logger.critical(
                    'failed storing resource usage measurements of activation %s of user %s into the database',
                    act.activationId, user_name, exc_info=True)

    def _get_resource_usage(self, cont_id, start, end):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(self.docker_mon_cfg.measurementsock)

        sock.sendall(json.dumps({
            'container': cont_id,
            'start': round(start / 1000, 3),
            'end': round(end / 1000, 3),
        }).encode())
        sock.shutdown(socket.SHUT_WR)

        meas = b''
        buff = sock.recv(4096)
        while buff:
            meas += buff
            buff = sock.recv(4096)

        sock.close()

        return json.loads(meas)

    def terminate(self):
        self.run_event.clear()


class TraceParsingException(Exception):
    pass


class InjectionException(Exception):
    pass
