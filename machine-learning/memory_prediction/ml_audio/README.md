Folders
--------------
    weka/res            Contains the results of Weka


Files
---------------
    weka/src/weka.py            The script to generate decision trees with Weka
    weka/src/print_result.py     The script to print result

I am using 4 algorithms (J48 (Weka), RandomTree (Weka), RandomForest (Weka), HoeffdingTree (Weka)) to predict the result.

I use cross validation to avoid overfitting.

Decision trees predict a cluster, not a numeric value. So I divide the memory interval [0, 2 048] MB into different cluster and we give the maximum memory of the cluster as a solution.

I divide into:

  - 64 clusters for a cluster of size 32 MB

  - 128 clusters for a cluster of size 16 MB

  - 256 clusters for a cluster of size 8 MB


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
|4            |pydub_effects                   |pydub                  |
|5            |plot_audio                      |matplotlib             |
|6            |fft                             |matplotlib             |
