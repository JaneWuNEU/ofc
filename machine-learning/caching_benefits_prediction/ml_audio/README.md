Folders
--------------
    weka/res            Contains the results of Weka


Files
---------------
    weka/src/weka.py             The script to generate decision trees with Weka
    weka/src/print_result.py     The script to print result

I am using 6 algorithms (J48 (Weka), RandomTree (Weka), RandomForest (Weka), HoeffdingTree (Weka)) to predict the result.

I use cross validation to avoid overfitting.

Decision trees predict a cluster, not a numeric value. I divide in two:

- 1: We use the cache
- 2: We do not use the cache


Use of weka
------------
  I am using weka from the command line. So you have to download [weka](https://prdownloads.sourceforge.net/weka/weka-3-9-4.zip) and change the path in my files to your weka-X/weka.jar file


To run weka
----------
```sh
(cd weka/src && python3 weka.py)
```

To print result
----------
```sh
(cd weka/src && python3 print_result.py)
```

Function
--------

|idFunction   |nameFunction                    | library               |
|------------:| ------------:                  | -------:              |
|1            |pydub_conver                    |pydub                  |
|2            |speech_recognition_google       |speech_recognition     |
|3            |speech_recognition_sphinx       |speech_recognition     |
|4            |pydub_effects_time              |pydub                  |
|5            |plot_audio                      |matplotlib             |
|6            |fft                             |matplotlib             |
