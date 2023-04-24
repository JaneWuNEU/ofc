Folders
--------------
    csv                 Contains a csv file for each function
    arff                Contains an arff file (file for weka) for each function, they are generated from features_audio/create_arff.py

Files
---------------
    extract.py          Simple script to extract data from general csv in order to generate a csv by function
    create_arff.py  Create arff files (weka files) from base CSV files

Extract infomation from CSV files which contain all informations from benchmark and create a csv file for each function
--------
```sh
python3 extract.py
```

Create arff files
-------

```sh
python3 create_arff.py
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

For an ARFF file
------

We have to do it in order:

    - @RELATIONSHIP function_name
    - @ATTRIBUTE name_of_the_feature_i type_of_the_feature_i (so here we will have all the features)
    - @ATTRIBUTE result_name {all possibilities of the result} (the result is the last one)
    - @DATA
    - comma-separated data.

