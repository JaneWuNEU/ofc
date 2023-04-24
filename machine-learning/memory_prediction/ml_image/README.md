Folders
--------------
    weka/res            Contains the results of Weka


Files
---------------
    weka/src/weka.py            The script to generate decision trees with Weka
    weka/src/print_result.py     The script to print result


I am using 5 algorithms (J48 (Weka), RandomTree (Weka), RandomForest (Weka), HoeffdingTree (Weka)) to predict the result.

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
