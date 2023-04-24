"""Module for the monitor threads.

Classes:

 * `DockerMonitorThread`: the class of the monitor threads;
 * `Measurement`: namedtuple to store one measurement of resource (memory and CPU) usage of a container at a given date.

Measurements are taken at most every `measurement_resolution` seconds, this is not an exact clock. There is a check in
the monitoring infinite loop that warns for missed measurements, saying "missed measurements for container [...]".
"""

import logging
import time
from collections import namedtuple
from threading import Event, Thread

from pycgroup import CGroup
from pycgroup.controllers import cpuacct as cgroup_cpu, memory as cgroup_memory

Measurement = namedtuple('Measurement', ['date', 'memory', 'cpu'])


class DockerMonitorThread(Thread):
    """Monitor thread.

    Monitor a Docker container used by OpenWhisk to run actions. The monitoring consists in storing periodic
    measurements of the memory and CPU usage of the container. Measurements are stored in a mutable data structure
    passed at creation time.

    ## Measurements

    Each measurement (a `Measurement` namedtuple) has its date stored as an absolute timestamp (in seconds,
    rounded to milliseconds); timestamps are not offset by the timestamp of the first measurement.

    Measurements may have None as memory or CPU value. This indicates failure reading the resource usage at this time.

    For memory, the measurements store the memory usage at the time (in bytes). It is the sum of the resident set size
    (RSS) and of the total mapped file size.

    For CPU, the measurements store the cumulative usage at the time (in seconds of CPU time, rounded to milliseconds)
    since the beginning of execution **of the container**. The monitor thread does not process the measurement, so you
    must process the values afterwards with at least the first of the following steps:

     * offset the starting CPU cumulative usage;
     * compute "instantaneous" CPU usages as percentage of CPU time: for two measurements c1 and c2 at times t1 and t2
        respectively, the instantaneous usage at (t1+t2)/2 is (c2-c1)/(t2-t1)

    ## Monitoring

    The monitoring is done by reading usage stats from the container's cgroup ("control groups", a feature of the Linux
    kernel). The thread is an infinite loop that reads the usage stats, stores them, then sleeps for some duration.

    The thread can be paused, and will block until resumed. It can also be terminated, which makes it return from its
    infinite loop.
    """

    def __init__(self, container_id, container_measurements, measurement_resolution):
        """Create a new monitor thread.

        :param container_id: the ID of the container to monitor (the name of its cgroup under Docker's root cgroup)
        :type container_id: str
        :param container_measurements: the mutable data structure used to store measurements (see below)
        :type container_measurements: list

        `container_measurements` must be mutable and support the `append` method, so it should be list-like. In
        practice, it might grow indefinitely if the monitored container is never destroyed, and the thread **will not
        shrink it**. Thus, it is a good idea to use a self-maintaining data structure such as a `deque` with a max
        length set.
        """
        name = 'monitor-' + container_id[:12]

        super().__init__(name=name, daemon=True)

        self.container_id = container_id

        # Take references to the cgroups, only for monitoring, no control (they are Docker's)
        self.mem_cgrp = CGroup(cgroup_memory, 'docker/' + self.container_id, reuse=True)
        self.cpu_cgrp = CGroup(cgroup_cpu, 'docker/' + self.container_id, reuse=True)

        self.measurements = container_measurements

        self.resolution = measurement_resolution

        self.missed = 0

        self.logger = logging.getLogger('monitor')

        self._monitor = Event()
        self._monitor.set()
        self._terminate = Event()

        # Used to suppress missed measurement check after resuming
        self.just_resumed = True

    def run(self):
        # both variables used to log only once in a row
        failing_memory = False
        failing_cpu = False

        while True:
            self._monitor.wait()
            if self._terminate.is_set():
                self.logger.info('terminate')
                break

            date = round(time.time(), 3)

            # check that we did not miss measurements
            if self.just_resumed:
                self.just_resumed = False
            else:
                previous = self.measurements[-1].date
                skipped = date - previous
                if skipped > 2 * self.resolution:
                    missed = skipped // self.resolution
                    self.missed += missed
                    self.logger.warning(
                        'missed %d measurements for container %s between %f and %f (total missed: %d/%d, %.1f%%)',
                        missed, self.container_id, previous, date, self.missed, len(self.measurements),
                        100 * self.missed / (len(self.measurements) + self.missed))

            try:
                memory = self.mem_cgrp.stat['total_rss'] + self.mem_cgrp.stat['total_mapped_file']
                failing_memory = False
            except OSError as err:
                if not failing_memory:
                    self.logger.error('failed reading memory usage of container %s: %s', self.container_id, err)
                    failing_memory = True
                memory = None
            try:
                cpu = round(self.cpu_cgrp.usage / 1000000000, 3)
                failing_cpu = False
            except OSError as err:
                if not failing_cpu:
                    self.logger.error('failed reading CPU usage of container %s: %s', self.container_id, err)
                    failing_cpu = True
                cpu = None

            self.measurements.append(Measurement(date, memory, cpu))

            time.sleep(self.resolution / 1000)

    def pause(self):
        """Pause the monitoring thread: no more measurements are stored until resumed."""
        self._monitor.clear()

    def resume(self):
        """Resume the paused monitoring thread."""
        self.just_resumed = True
        self._monitor.set()

    def terminate(self):
        """Terminate the monitoring thread."""
        # Resume the monitor by setting _monitor to unblock it
        self._monitor.set()
        self._terminate.set()
