FROM openwhisk/python3action:latest

# Installing SpeechRecognition via pip in the virtualenv that is embedded in the
# archive, results in an archive that OpenWhisk rejects because it is too big.
# So we circumvent this limitation by installing SpeechRecognition directly in the
# Docker runtime image
RUN pip install SpeechRecognition

RUN apk add --update swig pulseaudio-dev alsa-lib-dev && \
    pip install pocketsphinx

