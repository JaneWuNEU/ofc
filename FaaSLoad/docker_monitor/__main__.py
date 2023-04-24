"""Main module of the monitor.

Run the monitor as:
    python -m docker_monitor

This launches the measurements query server, as well as the notification server that creates monitor threads.

The module defines the following members:

 * SOCKET_BASEPATH: path to the directory of the sockets used by the monitor
 * SOCKET_PATH_NOTIFICATION: path of the notification socket; changes to this path must be reflected in the setup of
    OpenWhisk's invoker (see below)
 * SOCKET_PATH_MEASUREMENTS: path of the measurements query socket
 
The notification socket is written to by OpenWhisk's invoker to notify the monitor of its Docker operations. Thus, if
changing this path, it must also be updated in the Ansible playbook to deploy the invoker, in
"$OPENWHISK_HOME/ansible/roles/invoker/tasks/deploy.yml", under the task "set invoker volumes". Or course, all of this
also requires that the invoker has been modified to include the necessary changes to have it notify the monitor of its
Docker operations. This is done by including wrappers around the binaries of `docker` and `docker-runc` included in the
invoker's container, that send the notifications. The modifications are included in my "openwhisk" repository.
"""

import logging
import logging.config
import os
from threading import Thread

from utils import try_read_configuration
from . import DEFAULTS
from .measurements_server import MeasurementsQueryHandler, MeasurementsServer
from .notification import DockerNotificationHandler, DockerNotificationServer


def start_measurements_server(measurements, sock_path):
    with MeasurementsServer(measurements, sock_path, MeasurementsQueryHandler) as server:
        server.serve_forever()


def main():
    """Main function of the monitor."""
    conf = try_read_configuration(os.path.expanduser('~/.config/faasload/monitor.yml'), DEFAULTS)

    logger = logging.getLogger('main')
    logger.debug('Whisk Docker Monitor global configuration: %s', conf)

    measurements = {}
    monitor_workers = {}

    meas_svr = Thread(target=start_measurements_server, name='Thread-MeasurementsServer',
                      args=(measurements, os.path.expanduser(os.path.expandvars(conf['measurementserver'].sock))))
    meas_svr.start()

    with DockerNotificationServer(measurements, monitor_workers, conf['monitor'],
                                  os.path.expanduser(os.path.expandvars(conf['notification'].sock)),
                                  DockerNotificationHandler) as server:
        server.serve_forever()


if __name__ == '__main__':
    main()
