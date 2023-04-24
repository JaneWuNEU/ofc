import io
import os
from time import time

import numpy as np
import soundfile as sf
from swiftclient import Connection as SwiftConnection


def main(args):
    inputcont, outputcont = args['incont'], args['outcont']

    objectname = args['object']
    basename, _ = os.path.splitext(objectname)

    t0 = time()

    swiftconn = SwiftConnection(
        user=args['user'],
        key=args['key'],
        authurl=args['authurl'],
    )

    _, objectdata = swiftconn.get_object(inputcont, objectname)

    te = time()

    data, _ = sf.read(io.BytesIO(objectdata))

    fourier = np.fft.fft(data)
    outputdata = fourier.tobytes()

    tt = time()

    swiftconn.put_object(outputcont,
                         'fft_' + basename + '.dat',
                         contents=outputdata)

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
