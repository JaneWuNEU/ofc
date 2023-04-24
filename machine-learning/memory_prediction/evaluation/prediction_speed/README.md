# Evaluation: prediction speed

Evaluation the prediction speed of the models predicting memory usage, i.e. measure the time they take to classify.

Compile the scripts with:

```shell
javac -cp .:$PATH_TO_WEKA_JAR PredictionSpeed*.java
```

Then run each of them with:

```shell
# DATA_TYPE is either Audio, Image of Video
java -cp .:$PATH_TO_WEKA_JAR PredictionSpeed${DATA_TYPE} > prediction_speed_${DATA_TYPE}.txt
```

The scripts output their results to stdout, so redirect it to a file.
