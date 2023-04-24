"""Module for the measurements server.

Classes:

 * `MeasurementsServer`: the class of the measurements server
 * `MeasurementsQueryHandler`: the class of the measurements query handler
"""

import json
import logging
from datetime import datetime
from json import JSONDecodeError
from socketserver import StreamRequestHandler, UnixStreamServer

from .monitor import Measurement


class MeasurementsServer(UnixStreamServer):
    """Server for queries of measurements of resource usage by Docker containers of OpenWhisk actions.

    It is a `UnixStreamServer`, i.e. a stream (TCP) server listening on a UNIX socket.

    The main processing is done in the request handler `MeasurementsQueryHandler`. The server is only customized to
    store a reference to the shared data structure holding measurements.

    """

    def __init__(self, measurements, *args, **kwargs):
        self.measurements = measurements

        super().__init__(*args, **kwargs)


class MeasurementsQueryHandler(StreamRequestHandler):
    """Request handler for the measurements query server.

    Handle measurements queries made by a client program to fetch resource usage of Docker containers used by OpenWhisk
    to run actions.

    Queries of measurements are expected as small JSON objects:

        {"container": CONTAINER_ID,
         "start": ACTION_START,
         "end": ACTION_END}

    where CONTAINER_ID is the container ID, and ACTION_START and ACTION_END are the start and end timestamps (in
    seconds, precision up to the millisecond) of the action, i.e. the server will return all measurements about the
    specified container between those two dates.

    Measurements are returned as a JSON list of objects, each object being one measurement record like the following:

        {"date": TIMESTAMP,
         "memory": MEMORY,
         "cpu": CPU}

    where TIMESTAMP is the date of the measurement (in seconds, rounded to the millisecond), MEMORY is the memory usage
    of the container at this point (in bytes), and CPU is the cumulative CPU usage (in seconds of CPU, rounded to the
    millisecond) of the container up to this point **since the beginning of the queried timeslice**. For more
    information about the cumulative CPU usage, check the docstring of the `_handle_query` method, and the docstring of
    `DockerMonitorThread`.

    Note that for any measurement, "memory" or "cpu" may be null (Python `None`), indicating that the measurement failed
    at this date. A common occurrence is that the container is destroyed before the monitor is notified of it being
    destroyed by the invoker and has a chance to terminate the monitor thread, thus producing such failed measurements.
    """

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger('measurementserver')

        super().__init__(*args, **kwargs)

    def handle(self):
        try:
            query = json.load(self.rfile)
        except JSONDecodeError as err:
            self.logger.error('malformed JSON format for notification: %s', err)
            return

        try:
            self.wfile.write(json.dumps([m._asdict() for m in self._handle_query(query)]).encode())
        except KeyError:
            self.logger.error('malformed query:\n%s', query)
        except ValueError as err:
            self.logger.error(err)

    def _handle_query(self, query):
        """Handle the measurements query by fetching measurements in the given timeslice.

        CPU values of the measurements are processed by offsetting the CPU usage at the beginning of the timeslice:
        the container might have been used for a previous action, so at the start of the queried action the measurement
        of cumulative CPU usage might not be 0.

        This is the only processing done to the measurements. For instance, None values are not filtered out.
        """
        start = query['start']
        end = query['end']
        cid = query['container']

        self.logger.info('requested for container %s between %s and %s', cid,
                         datetime.fromtimestamp(start).isoformat(),
                         datetime.fromtimestamp(end).isoformat())

        try:
            meas = [m for m in self.server.measurements[cid] if start <= m.date <= end]
        except KeyError:
            raise ValueError(f'cannot find measurements for container {cid}')

        # Monitor threads store cumulative CPU usage of a container which means it may not start at 0 for a given action
        # if the container has been used for a previous action.
        cpu_offset = min([m for m in meas if m.cpu is not None], key=lambda m: m.date).cpu
        meas = [Measurement(m.date, m.memory, round(m.cpu - cpu_offset, 3)) for m in meas if m.cpu is not None]

        return meas
