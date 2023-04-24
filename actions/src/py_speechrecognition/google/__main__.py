import io
import os
from time import time

import speech_recognition as sr
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

    rec = sr.Recognizer()

    with sr.AudioFile(io.BytesIO(objectdata)) as audiosource:
        audio = rec.record(audiosource)
    result = rec.recognize_google(audio)

    tt = time()

    swiftconn.put_object(outputcont,
                         'transcript_' + basename + '.txt',
                         contents=result)

    tl = time()

    outputsize = len(result.encode('utf-8'))

    return {
        'outputsize': outputsize,
        'start_ms': t0 * 1000,
        'times': {
            'extract': (te - t0) * 1000,
            'transform': (tt - te) * 1000,
            'load': (tl - tt) * 1000,
        },
    }
