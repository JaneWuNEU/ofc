# Action runtimes

| Runtime | Processing | Language | Main dependency | Dependency package | Runtime image | Image content |
|--------:|------------|----------|-----------------|-------------------:|--------------:|--------------:|
| `js_sharp` | image | NodeJS | [Sharp](https://sharp.pixelplumbing.com/) | yes | no | N/A |
| `py_moviepy` | video | Python | [MoviePy](https://zulko.github.io/moviepy/) | yes\* | yes | nbd |
| `py_pydub` | audio | Python | [PyDub](https://pydub.com/) | yes | yes | n |
| `py_soundfile` | audio | Python | [SoundFile](pysoundfile.readthedocs.org) | yes | yes | n |
| `py_speechrecognition` | audio | Python | [SpeechRecognition](https://github.com/Uberi/speech_recognition#readme) | yes\* | yes | bd |
| `py_wand` | image | Python | [Wand](https://docs.wand-py.org/en/0.6.3/) | yes | yes | n |

## Notes

 * value "yes\*" in "Dependency package" indicates that the dependency package is only required because of the library to
   communicate with the Swift storage backend;
 * column "Image content" gives the reason(s) a custom runtime image is needed:
   * "n": the action needs native dependencies;
   * "b": the action needs build dependencies;
   * "d": the main dependency of the action must be embedded in the runtime image (instead of the dependency package).
