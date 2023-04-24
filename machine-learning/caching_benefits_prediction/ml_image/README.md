Folders
--------------
    weka/res            Contains the results of Weka


Files
---------------
    weka/src/weka.py            The script to generate decision trees with Weka
    weka/src/print_result.py     The script to print result

I am using 5 algorithms (J48 (Weka), RandomTree (Weka), RandomForest (Weka), HoeffdingTree (Weka)) to predict the result.

I use cross validation to avoid overfitting.

Decision trees predict a cluster, not a numeric value. I divide in two:

- 1: We use the cache
- 2: We do not use the cache


  Use of weka
  ------------
  I am using weka from the command line. So you have to download [weka](https://prdownloads.sourceforge.net/weka/weka-3-9-4.zip) and change the path in my files to your weka-X/weka.jar file

Function
--------

|folder    |idFunction   |nameFunction       | library      |
|---------:|------------:| ------------:     | -------:     |
|1         |1            |wand_denoise_time  |wand          |
|1         |2            |wand_edge_time     |wand          |
|1         |3            |wand_resize_time   |wand          |
|1         |4            |wand_rotate_time   |wand          |
|1         |5            |wand_sepia_time    |wand          |
|2         |1            |sharp_blur_time    |sharp         |
|2         |2            |sharp_sepia_time   |sharp         |
|2         |3            |sharp_resize_time  |sharp         |
|2         |4            |sharp_convert_time |sharp         |
|2         |5            |wand_blur_time     |wand          |
