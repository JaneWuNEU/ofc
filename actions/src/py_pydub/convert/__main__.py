import io
import os
from time import time

from pydub import AudioSegment
from swiftclient import Connection as SwiftConnection


def main(args):
    inputcont, outputcont = args['incont'], args['outcont']

    objectname, fmt = args['object'], args['format']
    basename, _ = os.path.splitext(objectname)

    t0 = time()

    swiftconn = SwiftConnection(
        user=args['user'],
        key=args['key'],
        authurl=args['authurl'],
    )

    _, objectdata = swiftconn.get_object(inputcont, objectname)

    te = time()

    loop = AudioSegment.from_file(io.BytesIO(objectdata))

    outputbuff = io.BytesIO()
    loop.export(outputbuff, format=fmt)
    outputdata = outputbuff.getbuffer()

    tt = time()

    swiftconn.put_object(outputcont, basename + '.' + fmt, contents=outputdata)

    tl = time()

    outputsize = len(outputdata)

    return {
        'outputsize': outputsize,
        'start_ms': t0 * 1000,
        'times': {
            'extract': (te - t0) * 1000,
            'transform': (tt - te) * 1000,
            'load': (tl - tt) * 1000,
        },
    }
