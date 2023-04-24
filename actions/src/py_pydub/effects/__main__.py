import io
import os
from time import time

from pydub import AudioSegment
from swiftclient import Connection as SwiftConnection


def main(args):
    inputcont, outputcont = args['incont'], args['outcont']

    objectname = args['object']
    _, fileformat = os.path.splitext(objectname)

    t0 = time()

    swiftconn = SwiftConnection(
        user=args['user'],
        key=args['key'],
        authurl=args['authurl'],
    )

    _, objectdata = swiftconn.get_object(inputcont, objectname)

    te = time()

    loop = AudioSegment.from_file(io.BytesIO(objectdata))

    loop2 = loop * 2

    fade_time = len(loop2) // 2
    faded = loop2.fade_in(fade_time).fade_out(fade_time)

    loop = loop2.reverse().pan(-0.5).overlay(faded.pan(0.5))

    outputbuff = io.BytesIO()
    loop.export(outputbuff, format=fileformat)
    outputdata = outputbuff.getbuffer()

    tt = time()

    swiftconn.put_object(outputcont, 'effects_' + objectname, contents=outputdata)

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
