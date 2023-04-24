from time import time

from swiftclient import Connection as SwiftConnection
from wand.image import Image


def main(args):
    inputcont, outputcont = args['incont'], args['outcont']

    # args comes from OpenWhisk, that processes the arguments are JSON, which means
    # that number-like arguments really are int of float in the code.
    # But we want a string for the "width", because it's actually a command for
    # Wand's transform() method.
    objectname, width = args['object'], str(args['width'])

    t0 = time()

    swiftconn = SwiftConnection(
        user=args['user'],
        key=args['key'],
        authurl=args['authurl'],
    )

    _, objectdata = swiftconn.get_object(inputcont, objectname)

    te = time()

    with Image(blob=objectdata) as img:
        img.transform(resize=width)

        tt = time()

        outputdata = img.make_blob('jpg')
        swiftconn.put_object(outputcont,
                             'resized_' + objectname,
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
