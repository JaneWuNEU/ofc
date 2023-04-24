import weka.classifiers.*;
import weka.classifiers.trees.*;
import weka.core.*;
import weka.experiment.*;
import java.io.*;
import weka.classifiers.meta.FilteredClassifier;
import weka.core.SerializationHelper;
import weka.core.converters.ConverterUtils.DataSource;
import weka.core.Instances;
import java.util.concurrent.TimeUnit;
import weka.classifiers.Classifier;
import weka.classifiers.Evaluation;
import weka.classifiers.evaluation.NominalPrediction;
import weka.classifiers.evaluation.Prediction;
import weka.classifiers.functions.SMO;
import weka.classifiers.functions.supportVector.PrecomputedKernelMatrixKernel;
import weka.core.DenseInstance;
import weka.core.Instance;
import weka.core.Instances;
import java.util.LinkedList;
import java.util.List;
import java.util.ArrayList;
import java.util.Collections;


public class PredictionSpeedAudio {
  public static String MODELS_BASEPATH = "../../ml_audio/weka/res";
  public static String DATA_BASEPATH = "../../data_audio/arff";

  public static void main(String[] args) throws Exception{

    J48 cls1_J48_64 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function1_64_output_model_J48_64.model");
    J48 cls1_J48_128 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function1_128_output_model_J48_128.model");
    J48 cls1_J48_256 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function1_256_output_model_J48_256.model");

    J48 cls2_J48_64 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function2_64_output_model_J48_64.model");
    J48 cls2_J48_128 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function2_128_output_model_J48_128.model");
    J48 cls2_J48_256 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function2_256_output_model_J48_256.model");

    J48 cls3_J48_64 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function3_64_output_model_J48_64.model");
    J48 cls3_J48_128 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function3_128_output_model_J48_128.model");
    J48 cls3_J48_256 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function3_256_output_model_J48_256.model");

    J48 cls4_J48_64 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function4_64_output_model_J48_64.model");
    J48 cls4_J48_128 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function4_128_output_model_J48_128.model");
    J48 cls4_J48_256 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function4_256_output_model_J48_256.model");

    J48 cls5_J48_64 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function5_64_output_model_J48_64.model");
    J48 cls5_J48_128 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function5_128_output_model_J48_128.model");
    J48 cls5_J48_256 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function5_256_output_model_J48_256.model");

    J48 cls6_J48_64 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function6_64_output_model_J48_64.model");
    J48 cls6_J48_128 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function6_128_output_model_J48_128.model");
    J48 cls6_J48_256 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function6_256_output_model_J48_256.model");

    DataSource source1_64 = new DataSource(DATA_BASEPATH + "/function1_64.arff");
    DataSource source2_64 = new DataSource(DATA_BASEPATH + "/function2_64.arff");
    DataSource source3_64 = new DataSource(DATA_BASEPATH + "/function3_64.arff");
    DataSource source4_64 = new DataSource(DATA_BASEPATH + "/function4_64.arff");
    DataSource source5_64 = new DataSource(DATA_BASEPATH + "/function5_64.arff");
    DataSource source6_64 = new DataSource(DATA_BASEPATH + "/function6_64.arff");

    DataSource source1_128 = new DataSource(DATA_BASEPATH + "/function1_128.arff");
    DataSource source2_128 = new DataSource(DATA_BASEPATH + "/function2_128.arff");
    DataSource source3_128 = new DataSource(DATA_BASEPATH + "/function3_128.arff");
    DataSource source4_128 = new DataSource(DATA_BASEPATH + "/function4_128.arff");
    DataSource source5_128 = new DataSource(DATA_BASEPATH + "/function5_128.arff");
    DataSource source6_128 = new DataSource(DATA_BASEPATH + "/function6_128.arff");

    DataSource source1_256 = new DataSource(DATA_BASEPATH + "/function1_256.arff");
    DataSource source2_256 = new DataSource(DATA_BASEPATH + "/function2_256.arff");
    DataSource source3_256 = new DataSource(DATA_BASEPATH + "/function3_256.arff");
    DataSource source4_256 = new DataSource(DATA_BASEPATH + "/function4_256.arff");
    DataSource source5_256 = new DataSource(DATA_BASEPATH + "/function5_256.arff");
    DataSource source6_256 = new DataSource(DATA_BASEPATH + "/function6_256.arff");


    Instances train1_64 = source1_64.getDataSet();
    Instances train2_64 = source2_64.getDataSet();
    Instances train3_64 = source3_64.getDataSet();
    Instances train4_64 = source4_64.getDataSet();
    Instances train5_64 = source5_64.getDataSet();
    Instances train6_64 = source6_64.getDataSet();

    Instances train1_128 = source1_128.getDataSet();
    Instances train2_128 = source2_128.getDataSet();
    Instances train3_128 = source3_128.getDataSet();
    Instances train4_128 = source4_128.getDataSet();
    Instances train5_128 = source5_128.getDataSet();
    Instances train6_128 = source6_128.getDataSet();

    Instances train1_256 = source1_256.getDataSet();
    Instances train2_256 = source2_256.getDataSet();
    Instances train3_256 = source3_256.getDataSet();
    Instances train4_256 = source4_256.getDataSet();
    Instances train5_256 = source5_256.getDataSet();
    Instances train6_256 = source6_256.getDataSet();

    if (train1_64.classIndex() == -1) {
        train1_64.setClassIndex(train1_64.numAttributes() - 1);
    }
    if (train1_128.classIndex() == -1) {
        train1_128.setClassIndex(train1_128.numAttributes() - 1);
    }
    if (train1_256.classIndex() == -1) {
        train1_256.setClassIndex(train1_256.numAttributes() - 1);
    }

    if (train2_64.classIndex() == -1) {
        train2_64.setClassIndex(train2_64.numAttributes() - 1);
    }
    if (train2_128.classIndex() == -1) {
        train2_128.setClassIndex(train2_128.numAttributes() - 1);
    }
    if (train2_256.classIndex() == -1) {
        train2_256.setClassIndex(train2_256.numAttributes() - 1);
    }

    if (train3_64.classIndex() == -1) {
        train3_64.setClassIndex(train3_64.numAttributes() - 1);
    }
    if (train3_128.classIndex() == -1) {
        train3_128.setClassIndex(train3_128.numAttributes() - 1);
    }
    if (train3_256.classIndex() == -1) {
        train3_256.setClassIndex(train3_256.numAttributes() - 1);
    }

    if (train4_64.classIndex() == -1) {
        train4_64.setClassIndex(train4_64.numAttributes() - 1);
    }
    if (train4_128.classIndex() == -1) {
        train4_128.setClassIndex(train4_128.numAttributes() - 1);
    }
    if (train4_256.classIndex() == -1) {
        train4_256.setClassIndex(train4_256.numAttributes() - 1);
    }

    if (train5_64.classIndex() == -1) {
        train5_64.setClassIndex(train5_64.numAttributes() - 1);
    }
    if (train5_128.classIndex() == -1) {
        train5_128.setClassIndex(train5_128.numAttributes() - 1);
    }
    if (train5_256.classIndex() == -1) {
        train5_256.setClassIndex(train5_256.numAttributes() - 1);
    }

    if (train6_64.classIndex() == -1) {
        train6_64.setClassIndex(train6_64.numAttributes() - 1);
    }
    if (train6_128.classIndex() == -1) {
        train6_128.setClassIndex(train6_128.numAttributes() - 1);
    }
    if (train6_256.classIndex() == -1) {
        train6_256.setClassIndex(train6_256.numAttributes() - 1);
    }

    double lStartTime;
    double lEndTime;
    double res;

    double label = 0;

    List<Double> time_1_64 = new ArrayList<>();
    List<Double> time_1_128 = new ArrayList<>();
    List<Double> time_1_256 = new ArrayList<>();

    List<Double> time_2_64 = new ArrayList<>();
    List<Double> time_2_128 = new ArrayList<>();
    List<Double> time_2_256 = new ArrayList<>();

    List<Double> time_3_64 = new ArrayList<>();
    List<Double> time_3_128 = new ArrayList<>();
    List<Double> time_3_256 = new ArrayList<>();

    List<Double> time_4_64 = new ArrayList<>();
    List<Double> time_4_128 = new ArrayList<>();
    List<Double> time_4_256 = new ArrayList<>();

    List<Double> time_5_64 = new ArrayList<>();
    List<Double> time_5_128 = new ArrayList<>();
    List<Double> time_5_256 = new ArrayList<>();

    List<Double> time_6_64 = new ArrayList<>();
    List<Double> time_6_128 = new ArrayList<>();
    List<Double> time_6_256 = new ArrayList<>();


    for (int i = 0; i < 1000; i++){
        lStartTime = System.nanoTime();
        label = cls1_J48_64.classifyInstance(train1_64.instance(i));
        lEndTime = System.nanoTime();
        res = lEndTime - lStartTime;
        time_1_64.add(res);
        lStartTime = System.nanoTime();
        label = cls1_J48_128.classifyInstance(train1_128.instance(i));
        lEndTime = System.nanoTime();
        res = lEndTime - lStartTime;
        time_1_128.add(res);
        lStartTime = System.nanoTime();
        label = cls1_J48_256.classifyInstance(train1_256.instance(i));
        lEndTime = System.nanoTime();
        res = lEndTime - lStartTime;
        time_1_256.add(res);

        lStartTime = System.nanoTime();
        label = cls2_J48_64.classifyInstance(train2_64.instance(i));
        lEndTime = System.nanoTime();
        res = lEndTime - lStartTime;
        time_2_64.add(res);
        lStartTime = System.nanoTime();
        label = cls2_J48_128.classifyInstance(train2_128.instance(i));
        lEndTime = System.nanoTime();
        res = lEndTime - lStartTime;
        time_2_128.add(res);
        lStartTime = System.nanoTime();
        label = cls2_J48_256.classifyInstance(train2_256.instance(i));
        lEndTime = System.nanoTime();
        res = lEndTime - lStartTime;
        time_2_256.add(res);

        lStartTime = System.nanoTime();
        label = cls3_J48_64.classifyInstance(train3_64.instance(i));
        lEndTime = System.nanoTime();
        res = lEndTime - lStartTime;
        time_3_64.add(res);
        lStartTime = System.nanoTime();
        label = cls3_J48_128.classifyInstance(train3_128.instance(i));
        lEndTime = System.nanoTime();
        res = lEndTime - lStartTime;
        time_3_128.add(res);
        lStartTime = System.nanoTime();
        label = cls3_J48_256.classifyInstance(train3_256.instance(i));
        lEndTime = System.nanoTime();
        res = lEndTime - lStartTime;
        time_3_256.add(res);

        lStartTime = System.nanoTime();
        label = cls4_J48_64.classifyInstance(train4_64.instance(i));
        lEndTime = System.nanoTime();
        res = lEndTime - lStartTime;
        time_4_64.add(res);
        lStartTime = System.nanoTime();
        label = cls4_J48_128.classifyInstance(train4_128.instance(i));
        lEndTime = System.nanoTime();
        res = lEndTime - lStartTime;
        time_4_128.add(res);
        lStartTime = System.nanoTime();
        label = cls4_J48_256.classifyInstance(train4_256.instance(i));
        lEndTime = System.nanoTime();
        res = lEndTime - lStartTime;
        time_4_256.add(res);

        lStartTime = System.nanoTime();
        label = cls5_J48_64.classifyInstance(train5_64.instance(i));
        lEndTime = System.nanoTime();
        res = lEndTime - lStartTime;
        time_5_64.add(res);
        lStartTime = System.nanoTime();
        label = cls5_J48_128.classifyInstance(train5_128.instance(i));
        lEndTime = System.nanoTime();
        res = lEndTime - lStartTime;
        time_5_128.add(res);
        lStartTime = System.nanoTime();
        label = cls5_J48_256.classifyInstance(train5_256.instance(i));
        lEndTime = System.nanoTime();
        res = lEndTime - lStartTime;
        time_5_256.add(res);

        lStartTime = System.nanoTime();
        label = cls6_J48_64.classifyInstance(train6_64.instance(i));
        lEndTime = System.nanoTime();
        res = lEndTime - lStartTime;
        time_6_64.add(res);
        lStartTime = System.nanoTime();
        label = cls6_J48_128.classifyInstance(train6_128.instance(i));
        lEndTime = System.nanoTime();
        res = lEndTime - lStartTime;
        time_6_128.add(res);
        lStartTime = System.nanoTime();
        label = cls6_J48_256.classifyInstance(train6_256.instance(i));
        lEndTime = System.nanoTime();
        res = lEndTime - lStartTime;
        time_6_256.add(res);

    }


    Collections.sort(time_1_64);
    Collections.sort(time_1_128);
    Collections.sort(time_1_256);

    Collections.sort(time_2_64);
    Collections.sort(time_2_128);
    Collections.sort(time_2_256);

    Collections.sort(time_3_64);
    Collections.sort(time_3_128);
    Collections.sort(time_3_256);

    Collections.sort(time_4_64);
    Collections.sort(time_4_128);
    Collections.sort(time_4_256);

    Collections.sort(time_5_64);
    Collections.sort(time_5_128);
    Collections.sort(time_5_256);

    Collections.sort(time_6_64);
    Collections.sort(time_6_128);
    Collections.sort(time_6_256);

    System.out.println("J48;1;64");
    for (int i = 0; i < 1000; i++){
        System.out.print(time_1_64.get(i));
        System.out.print(", ");
    }
    System.out.println("\nJ48;1;128");
    for (int i = 0; i < 1000; i++){
        System.out.print(time_1_128.get(i));
        System.out.print(", ");
    }
    System.out.println("\nJ48;1;256");
    for (int i = 0; i < 1000; i++){
        System.out.print(time_1_256.get(i));
        System.out.print(", ");
    }

    System.out.println("\nJ48;2;64");
    for (int i = 0; i < 1000; i++){
        System.out.print(time_2_64.get(i));
        System.out.print(", ");
    }
    System.out.println("\nJ48;2;128");
    for (int i = 0; i < 1000; i++){
        System.out.print(time_2_128.get(i));
        System.out.print(", ");
    }
    System.out.println("\nJ48;2;256");
    for (int i = 0; i < 1000; i++){
        System.out.print(time_2_256.get(i));
        System.out.print(", ");
    }

    System.out.println("\nJ48;3;64");
    for (int i = 0; i < 1000; i++){
        System.out.print(time_3_64.get(i));
        System.out.print(", ");
    }
    System.out.println("\nJ48;3;128");
    for (int i = 0; i < 1000; i++){
        System.out.print(time_3_128.get(i));
        System.out.print(", ");
    }
    System.out.println("\nJ48;3;256");
    for (int i = 0; i < 1000; i++){
        System.out.print(time_3_256.get(i));
        System.out.print(", ");
    }

    System.out.println("\nJ48;4;64");
    for (int i = 0; i < 1000; i++){
        System.out.print(time_4_64.get(i));
        System.out.print(", ");
    }
    System.out.println("\nJ48;4;128");
    for (int i = 0; i < 1000; i++){
        System.out.print(time_4_128.get(i));
        System.out.print(", ");
    }
    System.out.println("\nJ48;4;256");
    for (int i = 0; i < 1000; i++){
        System.out.print(time_4_256.get(i));
        System.out.print(", ");
    }

    System.out.println("\nJ48;5;64");
    for (int i = 0; i < 1000; i++){
        System.out.print(time_5_64.get(i));
        System.out.print(", ");
    }
    System.out.println("\nJ48;5;128");
    for (int i = 0; i < 1000; i++){
        System.out.print(time_5_128.get(i));
        System.out.print(", ");
    }
    System.out.println("\nJ48;5;256");
    for (int i = 0; i < 1000; i++){
        System.out.print(time_5_256.get(i));
        System.out.print(", ");
    }

    System.out.println("\nJ48;6;64");
    for (int i = 0; i < 1000; i++){
        System.out.print(time_6_64.get(i));
        System.out.print(", ");
    }
    System.out.println("\nJ48;6;128");
    for (int i = 0; i < 1000; i++){
        System.out.print(time_6_128.get(i));
        System.out.print(", ");
    }
    System.out.println("\nJ48;6;256");
    for (int i = 0; i < 1000; i++){
        System.out.print(time_6_256.get(i));
        System.out.print(", ");
    }
  }
}
