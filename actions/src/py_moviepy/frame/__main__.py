import os
from time import time

from moviepy.editor import VideoFileClip
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

    # VideoPy is a very bad library that can only read from files, asking for a
    # filename. So we need to actually write the video to a file, have it read it,
    # and then write the result video to another file...
    with open(objectname, 'wb') as inputfile:
        inputfile.write(objectdata)

    clip = VideoFileClip(objectname)

    clip = clip.save_frame('frame.jpg', t=5)

    tt = time()

    with open('frame.jpg', 'rb') as outputfile:
        swiftconn.put_object(outputcont,
                             'frame_' + basename + '.jpg',
                             contents=outputfile)

    tl = time()

    outputsize = os.path.getsize('frame.jpg')

    return {
        'outputsize': outputsize,
        'start_ms': t0 * 1000,
        'times': {
            'extract': (te - t0) * 1000,
            'transform': (tt - te) * 1000,
            'load': (tl - tt) * 1000,
        },
    }
