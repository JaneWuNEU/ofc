"""OpenWhisk Docker monitor --- monitor to Apache OpenWhisk's Docker containers that run actions.

Run the monitor as:
    python -m docker_monitor

See docstring of `__main__` for more usage information. See below for architecture and API overview.

## Architecture

The monitor's main task is to collect CPU and memory usage data of Docker containers that OpenWhisk uses to run its
actions. Then, that data can be queried from another program; typically, this is the dataset generator.

It has three components:

 1. a notification server: the monitor listens on a socket mounted in OpenWhisk's invoker container, that the invoker
    writes to in order to notify the monitor of its container operations (run, rm, pause, resume);
 2. monitor threads: the notifications about container operations are interpreted by the notification server, which then
    manages monitor threads to actually monitor action containers;
 3. a measurements server: monitor threads store usage data continuously, that can be retrieved by programs clients to
    the monitor via the measurements query server, which listens on a socket to server measurements of CPU and memory
    usage for a given container and time slice.

More information about each component can be found in their respective sub-modules `notification`, `monitor` and
`measurements_server`.

The monitor as a whole works as follows:

 1. upon execution, its notification server listens its socket, and its measurements server on its other socket, waiting
    for notifications from OpenWhisk's invoker;
 2. when an OpenWhisk action is invoked, the invoker runs a container, and thus notifies the monitor of a container
    creation, following which the notification server spawns a new monitor thread for this container;
 3. unless paused or destroyed (see next steps), the monitor thread continuously stores CPU and memory usage of the
    target container at regular intervals;
 4. after the action finishes, OpenWhisk's invoker pauses the container and sends the adequate notification, so the
    notification server pauses the thread that monitors the paused container;
 5. a main program using the monitor will typically send a request to the measurements server on its socket at this
    point, in order to retrieve resource usage data about the action that just ran, providing the container ID as well
    as the time slice of interest (the execution of the action);
 6. if an OpenWhisk action is invoked that can use the same container, OpenWhisk resumes it, sending a notification and
    the notification server also resumes the monitoring thread;
 7. eventually, the container is destroyed by OpenWhisk's invoker, which also sends a notification to the notification
    server that destroys the monitoring thread attached to the container.

Summary: at the center is the notification server that manages monitor threads depending on notifications sent by
OpenWhisk's invoker; monitor threads store resource usage data of OpenWhisk's action containers, which can be queried
via the measurements server.

## API

While the monitor can be run as explained at the beginning, you can use its components manually. See `__main__` for an
example. See each corresponding module for more information on each component.

Of importance is that two data structures are shared among all threads:

 * `measurements`: a dictionary mapping container IDs to their measurements;
 * `monitor_workers`: a dictionary mapping container IDs to their monitor threads.

Only the notification server modifies these data structures, by adding and removing mappings. The measurements server
only reads `measurements`; and each monitor thread is only given the value (a mutable data structure) kept in
`measurements` to store the measurements of the corresponding container, so this is thread-safe.

### Notification server

The notification server in `notification` is the class `DockerNotificationServer`. It subclasses `UnixStreamServer`,
i.e. it is a stream (TCP) server listening on a UNIX socket. Requests are handled by a matching subclass of
`StreamRequestHandler` named `DockerNotificationHandler`.

It is the most central component of the monitor, so you can simply run its `server_forever` method in the main thread to
monitor indefinitely.

### Monitor threads

The notification server spawns threads of class `DockerMonitorThread`, that execute infinite loops of monitoring until
they are made to exit by the notification server. They are stored in the shared data structure `monitor_workers`.

### Measurements server

The measurements server in `measurements_server` is the class `MeasurementsServer`. Like the notification server, it
subclasses ` UnixStreamServer`. Requests are handled by a matching subclass of `StreamRequestHandler` named
`MeasurementsQueryHandler`.
"""

from collections import namedtuple

NotificationConfiguration = namedtuple('NotificationConfiguration', ['sock'])
MonitorConfiguration = namedtuple('MonitorConfiguration', ['resolution', 'maxage'])
MeasurementServerConfiguration = namedtuple('MeasurementConfiguration', ['sock'])

# In this structure, None means that the value is mandatory in the configuration file
DEFAULTS = {
    'notification': NotificationConfiguration(
        sock='/run/wdm/notif',
    ),
    'monitor': MonitorConfiguration(
        resolution=0.01,
        maxage=1800,
    ),
    'measurementserver': MeasurementServerConfiguration(
        sock='/run/wdm/meas',
    ),
}
