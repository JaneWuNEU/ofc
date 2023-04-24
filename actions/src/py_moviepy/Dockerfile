FROM openwhisk/python3action:latest

RUN apk add ffmpeg

# libjpeg and zlib are build dependencies for Pillow, itself a dependency for
# moviepy
RUN apk add --update jpeg-dev zlib-dev && \
    pip install moviepy

