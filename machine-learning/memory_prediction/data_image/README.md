Folders
--------------
    csv                 Contains a csv file for each function
    arff                Contains an arff file (file for weka) for each function, they are generated from features_image/create_arff.py

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

|idFunction   |nameFunction       | library      |
|------------:| ------------:     | -------:     |
|1            |sharp_blur         |sharp         |
|2            |sharp_sepia        |sharp         |
|3            |sharp_resize       |sharp         |
|4            |sharp_convert      |sharp         |
|5            |wand_blur          |wand          |
|6            |wand_denoise       |wand          |
|7            |wand_edge          |wand          |
|8            |wand_resize        |wand          |
|9            |wand_rotate        |wand          |
|10           |wand_sepia         |wand          |

For an ARFF file
------

We have to do it in order:

    - @RELATIONSHIP function_name
    - @ATTRIBUTE name_of_the_feature_i type_of_the_feature_i (so here we will have all the features)
    - @ATTRIBUTE result_name {all possibilities of the result} (the result is the last one)
    - @DATA
    - comma-separated data.

