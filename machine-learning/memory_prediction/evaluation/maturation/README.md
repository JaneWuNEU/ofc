Idea
----------
The goal is to know when our model is mature. For that we will train different model with a different number of data ([10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000]). And we will look at the results to know from what number of data our model is mature.


Files
---------------
    data_audio/create_train_file.py          Script to create train arff file with different size and a test arff file
    data_image/create_train_file.py          Script to create train arff file with different size and a test arff file

    audio/weka.py                            Script to generate decision trees with Weka and test files
    audio/print_result.py                    Script to print results
    image/weka.py                            Script to generate decision trees with Weka and test files
    image/print_result.py                    Script to print results

Execution order
------------------------------
```sh
cd data_{image, audio}

python3 create_train_file.py
```
To have all train and test files

```sh
cd {image, audio}

python3 weka.py
python3 print_result.py
```
to have all modeles and test files and extract informations with print_result

For others functions
-----------------

If you want to use this scripts for other functions. You need to change some parts identify by "#FOROTHERSFUNCTIONS"

- create_train_file take an arff file complete of each function and create one test file and 36 train file with differents size ([10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000]).
So you need to change headers and PATH

- weka.py will generate tree and tests files with the train and test files generated by create_train_file.py. You just need to change the path for arff file and the path for every files generates by weka

- print_result.py print the result of each test of weka with differents data generated by weka.py. You just need to change the path
