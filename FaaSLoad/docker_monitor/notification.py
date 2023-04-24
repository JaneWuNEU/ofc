"""Module for the notification server.

Classes:

 * `DockerNotificationServer`: the class of the notification server;
 * `DockerNotificationHandler`: the class of the notification handler.

The notification server is the one creating data structures to store measurements. It uses deques with a maximum length
set: the behavior is that when the maximum number of measurements are stored, oldest measurements are replaced by newer
ones. `monitor_cfg.maxage` should be high enough that the program using the monitor has time to request the
measurements of an action execution before the oldest are replaced by new measurements in case a new action is executed
in the same container.
"""

import json
import logging
from collections import deque
from json import JSONDecodeError
from math import ceil
from socketserver import StreamRequestHandler, UnixStreamServer

from .monitor import DockerMonitorThread


class DockerNotificationServer(UnixStreamServer):
    """Server for notifications about Docker operations made by OpenWhisk's invoker.

    It is a `UnixStreamServer`, i.e. a stream (TCP) server listening on a UNIX socket.

    The main processing is done in the request handler `DockerNotificationHandler`. The server is only customized to
    store references to the shared data structures holding measurements and reference to monitor threads.
    """

    def __init__(self, measurements, monitor_workers, monitor_cfg, *args, **kwargs):
        self.measurements = measurements
        self.monitor_workers = monitor_workers
        self.monitor_cfg = monitor_cfg

        super().__init__(*args, **kwargs)


class DockerNotificationHandler(StreamRequestHandler):
    """Request handler for the notification server.

    Handle notifications sent by OpenWhisk's invoker about its Docker container operations (run, rm, pause, resume).

    In some way, this is the central control point of the monitor because monitor threads are managed by this handler:

     * container creation: spawn monitor thread;
     * container pause: pause monitor thread;
     * container resuming: resume monitor thread;
     * container destruction: terminate monitor thread.


    Notifications are expected as small JSON objects:

        {"action": ACTION,
         "container": CONTAINER_ID}

    where ACTION is the container operation: one of "run", "rm", "pause" and "resume"; and CONTAINER_ID is the container
    ID as returned by Docker, specified on the command line by the invoker, and also as found in Docker's cgroup
    hierarchy for monitoring (see documentation in `monitor`).
    """

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger('dockernotifications')

        super().__init__(*args, **kwargs)

    def handle(self):
        try:
            notif = json.load(self.rfile)
        except JSONDecodeError as err:
            self.logger.error('malformed JSON format for notification: %s', err)
            return

        try:
            self._handle_notification(notif)
        except KeyError:
            self.logger.error('malformed notification:\n%s', notif)
        except ValueError as err:
            self.logger.error(err)

    def _handle_notification(self, notif):
        """Handle the notification by managing monitor threads.

        Depending on the notified action, create, terminate, pause or resume the thread monitoring the specified
        container. Also, create or remove deques in the shared `measurements` data structure, and add to or remove
        monitor threads from the shared `monitor_workers` data structure (references taken from the server).
        """
        action = notif['action']
        cid = notif['container']

        if action == 'run':
            if cid in self.server.measurements:
                raise ValueError(f'container {cid} already running')

            # Measurements for a given container are deques used as circular lists: new measurements are added with
            # `append`, and will replace the oldest ones when maxlen is reached.
            # The measurement server will fetch measurements in a given interval simply by iterating over the deque, and
            # no measurement is ever removed (only replaced by newer ones).
            measurements = deque(maxlen=ceil(self.server.monitor_cfg.maxage / self.server.monitor_cfg.resolution))
            self.server.measurements[cid] = measurements
            monitor_thread = DockerMonitorThread(cid, measurements, self.server.monitor_cfg.resolution)
            self.server.monitor_workers[cid] = monitor_thread
            monitor_thread.start()

            self.logger.info('run container %s', cid)
        elif action == 'rm':
            # We do not keep measurements for removed containers, relying on the fact that OpenWhisk keeps containers
            # around after their use so our client has time to fetch its measurements
            try:
                monitor_thread = self.server.monitor_workers.pop(cid)
                monitor_thread.terminate()
                monitor_thread.join(timeout=5)
                if monitor_thread.is_alive():
                    self.logger.warning('monitor thread for container %s is now zombie', cid)
                del self.server.measurements[cid]
            except KeyError:
                raise ValueError(f'cannot find container {cid} for deletion')

            self.logger.info('deleted container %s', cid)
        elif action == 'pause':
            try:
                self.server.monitor_workers[cid].pause()
            except KeyError:
                raise ValueError(f'cannot find container {cid} for pause')

            self.logger.info('paused container %s', cid)
        elif action == 'resume':
            try:
                self.server.monitor_workers[cid].resume()
            except KeyError:
                raise ValueError(f'cannot find container {cid} for resuming')

            self.logger.info('resumed container %s', cid)
        else:
            raise ValueError(f'unrecognized action "{action}"')
