# FaaSCache: machine learning study

This repository contains all scripts and data used in our study to determine the best machine learning (ML) algorithm to be used in [FaaSCache](https://gitlab.com/lenapster/faascache), as well as scripts and data for its evaluation.

In this repository, you will find:

 * a base dataset of function executions;
 * scripts to train models using several ML algorithms from the dataset, and produce evaluation data and figures;
 * scripts to produce evaluation data and figures about the maturation quickness and the prediction speed of the selected algorithm.

The next section explains how to reproduce the evaluations included in the paper.
The last section recalls the purpose of this repository in the context of our paper "FaaSCache" and lists its content.

## Results reproduction

We evaluated ML algorithms out of FaaSCache, from a dataset of function executions, because the purpose was to select the best algorithm to predict memory usage, and then validate this choice according to accuracy, prediction speed and maturation quickness.

In this section, you will go through:

 * processing data from the dataset;
 * training the memory prediction models;
 * evaluating the models by producing the figures in the paper;
 * evaluate the J48 models (i.e. the models trained using the selected algorithm) with regards to maturation quickness and prediction speed.

For the sake of simplicity, we only go over the steps for the memory prediction models.
Thus, change directory into "memory\_prediction" before following the instructions below.
To reproduce the results about the models used to predict caching benefits, run the same scripts but from the directory "caching\_benefits\_prediction", and change the results directory to "results/caching" instead of "results/memory" when redirecting script outputs (see below).

### Installation

Our ML work uses the Java ML library [Weka](https://www.cs.waikato.ac.nz/~ml/weka/).
So first, you must "install" Weka: download and extract the JAR archives as shown below.

```sh
wget https://prdownloads.sourceforge.net/weka/weka-3-8-5-azul-zulu-linux.zip
unzip weka-3-8-5-azul-zulu-linux.zip 
```

Export the path to Weka's main JAR ("weka.jar") under `$WEKA_JAR`:

```sh
export WEKA_JAR="/absolute/path/to/weka-3-9-5/weka.jar"
```

This way, the scripts used below can call Weka's code.

To use the final Jupyter Notebook to produce evaluation figures as presented in the paper, a few Python dependencies are required.
The virtual environment for them can be installed with pipenv, so install pip, pipenv, and finally the dependencies for the evaluation:

```sh
# install pip, i.e. on Ubuntu 20.04/Debian Buster
sudo apt install pipenv
# call pipenv to install dependencies
pipenv install
```

### Data processing

There is a preliminary step of data processing: from the raw dataset, produce input files for Weka and extract ML features from the input files of the functions.

Because ML features are different depending on the kind of inputs that a function accepts, there are 2 versions of each script in the following code excerpts, one per kind:

 * audio
 * image

Replace `KIND` with any of the three kind names above.

Evaluation and paper mention the kind "video": we evaluated on video processing functions, sadly most scripts and base data have been lost.
It means that you cannot run the scripts on the "video" kind, however the final Jupyter Notebook displaying evaluation results include results for the "video" kind.
The results we used in the paper are included in the repository, as well as the trained models.

First, extract per-function data from the dataset:

```sh
cd data_KIND
python3 extract.py
```

Then, create input files (format ARFF) for Weka:

```sh
cd data_KIND
python3 create_arff.py
```

### Model training

Now, train the models: there is one model per function, and we train models using several algorithms for comparison (namely `HoeffdingTree`, `J48`, `RandomForest` and `RandomTree`).

```sh
cd ml_KIND/weka/src
python3 weka.py
```

### Generate raw result data

Produce evaluation results of the models' accuracy: first global statistics, and then predictions to evaluate error dispersion.

```sh
cd ml_KIND/weka/src
python3 print_stats.py > ../../../../results/memory/models_accuracy/KIND.csv
python3 print_prediction_tests.py > ../../../../results/memory/predictions/KIND.csv
```

To evaluate the chosen algorithm J48, first change directory to "evaluation". There are two subfolders:

 * "maturation": evaluate the maturation quickness of the models;
 * "prediction\_speed": evaluate the prediction speed of the models.

#### Maturation

The principle of this experiment is to create training sets of growing sizes, to train models on them and then evaluate each model to determine the minimum set size so that the models are "accurate enough" as defined in the paper.

Again, instructions are to be followed per input kind.

First, create training sets:

```sh
cd data_KIND
python3 create_train_file.py
```

Then, train and evaluate all the models for each function and each set size:

```sh
cd KIND
python3 weka.py
```

Finally, produce evaluation results:

```sh
cd KIND
python3 print-result.py > ../../../../results/memory/maturation/KIND.csv
```

#### Prediction speed

The experiment is much simpler: train models and then make many predictions with them, measuring the time they take.

Again, instructions are to be followed per input kind.

This time, this is Java code, so you need to compile them first:

```sh
javac -cp ".:$WEKA_JAR" PredictionSpeedKIND.java
```

And then execute them, saving the raw experiment data to a file:

```sh
java -cp ".:$WEKA_JAR" PredictionSpeedKIND.java > ../../../results/memory/prediction_speed/image.txt
```

### Generate figures and data for the paper

Finally, use the Jupyter Notebook "evaluation.ipynb" to process the evaluate data and produce the figures displayed in the paper:

```sh
# run Jupyter kernel: a browser should open, just click on the notebook and run it
# use pipenv run to run it from the virtual environment where dependencies where installed
pipenv run jupyter notebook
```

## General information

As part of FaaSCache's opportunistic caching system, the amount of memory that is reserved but unused by the platform's tenants (the "opportunity" from the title) must be predicted.
This free amount is then allocated to the cache.
Furthermore, the system also needs to predict whether caching data will actually benefit a function's invocation.

Thus, we experimented on machine learning (ML) algorithms to achieve those prediction goals.
For a given FaaS function, we can predict the amount of memory it will need, based on its input data and invocation parameters; as well as whether caching its data will be useful.
In particular, we extract features from the input data, so the process depends on the king of the input: we currently support audio, image and video.

## Repository structure

The folder structure reflects both ML goals of prediction the available memory amount, and the caching benefits.
Subfolders most often reflect the fact that we must adapt our ML process to the input kind of the functions (audio, image or video).

 * "caching\_benefits\_prediction": scripts related to predicting the benefits of caching data (model training and evaluation)
 * "memory\_prediction": scripts related to predicting the memory usage of functions (model training and evaluation, as well as advanced evaluation of the chosen algorithm)
 * "data": base data used in our experiments (see below)

In addition, a Jupyter Notebook "evaluation.ipynb" allows to produce the figures as presented in the paper.

The directory "data" includes the base data for our experiments.
This is a dataset that we generated, that contains executions of representative FaaS functions.
Data include memory and CPU usage of the functions, and also records their inputs and parameters so that ML models can be trained from them.

The two main folders "caching\_benefits\_prediction" and "memory\_prediction" are subdivided as follows:

 * "data\_KIND": intermediate data extracted and processed from "data"
 * "features\_KIND": intermediate data (features of the function executions' inputs) extracted and processed from "data"
 * "ml\_KIND": scripts to train and evaluate ML models

For the memory prediction part, an additional folder "evaluation" includes scripts to evaluate our chosen ML algorithm, J48, with regards to prediction speed and maturation quickness.
