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


public class PredictionSpeedImage {
    public static String MODELS_BASEPATH = "../../ml_image/weka/res";
    public static String DATA_BASEPATH = "../../data_image/arff";

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

        J48 cls7_J48_64 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function7_64_output_model_J48_64.model");
        J48 cls7_J48_128 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function7_128_output_model_J48_128.model");
        J48 cls7_J48_256 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function7_256_output_model_J48_256.model");

        J48 cls8_J48_64 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function8_64_output_model_J48_64.model");
        J48 cls8_J48_128 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function8_128_output_model_J48_128.model");
        J48 cls8_J48_256 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function8_256_output_model_J48_256.model");

        J48 cls9_J48_64 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function9_64_output_model_J48_64.model");
        J48 cls9_J48_128 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function9_128_output_model_J48_128.model");
        J48 cls9_J48_256 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function9_256_output_model_J48_256.model");

        J48 cls10_J48_64 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function10_64_output_model_J48_64.model");
        J48 cls10_J48_128 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function10_128_output_model_J48_128.model");
        J48 cls10_J48_256 = (J48) weka.core.SerializationHelper.read(MODELS_BASEPATH + "/function10_256_output_model_J48_256.model");


        DataSource source1_64 = new DataSource(DATA_BASEPATH + "/function1_64.arff");
        DataSource source2_64 = new DataSource(DATA_BASEPATH + "/function2_64.arff");
        DataSource source3_64 = new DataSource(DATA_BASEPATH + "/function3_64.arff");
        DataSource source4_64 = new DataSource(DATA_BASEPATH + "/function4_64.arff");
        DataSource source5_64 = new DataSource(DATA_BASEPATH + "/function5_64.arff");
        DataSource source6_64 = new DataSource(DATA_BASEPATH + "/function6_64.arff");
        DataSource source7_64 = new DataSource(DATA_BASEPATH + "/function7_64.arff");
        DataSource source8_64 = new DataSource(DATA_BASEPATH + "/function8_64.arff");
        DataSource source9_64 = new DataSource(DATA_BASEPATH + "/function9_64.arff");
        DataSource source10_64 = new DataSource(DATA_BASEPATH + "/function10_64.arff");

        DataSource source1_128 = new DataSource(DATA_BASEPATH + "/function1_128.arff");
        DataSource source2_128 = new DataSource(DATA_BASEPATH + "/function2_128.arff");
        DataSource source3_128 = new DataSource(DATA_BASEPATH + "/function3_128.arff");
        DataSource source4_128 = new DataSource(DATA_BASEPATH + "/function4_128.arff");
        DataSource source5_128 = new DataSource(DATA_BASEPATH + "/function5_128.arff");
        DataSource source6_128 = new DataSource(DATA_BASEPATH + "/function6_128.arff");
        DataSource source7_128 = new DataSource(DATA_BASEPATH + "/function7_128.arff");
        DataSource source8_128 = new DataSource(DATA_BASEPATH + "/function8_128.arff");
        DataSource source9_128 = new DataSource(DATA_BASEPATH + "/function9_128.arff");
        DataSource source10_128 = new DataSource(DATA_BASEPATH + "/function10_128.arff");

        DataSource source1_256 = new DataSource(DATA_BASEPATH + "/function1_256.arff");
        DataSource source2_256 = new DataSource(DATA_BASEPATH + "/function2_256.arff");
        DataSource source3_256 = new DataSource(DATA_BASEPATH + "/function3_256.arff");
        DataSource source4_256 = new DataSource(DATA_BASEPATH + "/function4_256.arff");
        DataSource source5_256 = new DataSource(DATA_BASEPATH + "/function5_256.arff");
        DataSource source6_256 = new DataSource(DATA_BASEPATH + "/function6_256.arff");
        DataSource source7_256 = new DataSource(DATA_BASEPATH + "/function7_256.arff");
        DataSource source8_256 = new DataSource(DATA_BASEPATH + "/function8_256.arff");
        DataSource source9_256 = new DataSource(DATA_BASEPATH + "/function9_256.arff");
        DataSource source10_256 = new DataSource(DATA_BASEPATH + "/function10_256.arff");


        Instances train1_64 = source1_64.getDataSet();
        Instances train2_64 = source2_64.getDataSet();
        Instances train3_64 = source3_64.getDataSet();
        Instances train4_64 = source4_64.getDataSet();
        Instances train5_64 = source5_64.getDataSet();
        Instances train6_64 = source6_64.getDataSet();
        Instances train7_64 = source7_64.getDataSet();
        Instances train8_64 = source8_64.getDataSet();
        Instances train9_64 = source9_64.getDataSet();
        Instances train10_64 = source10_64.getDataSet();

        Instances train1_128 = source1_128.getDataSet();
        Instances train2_128 = source2_128.getDataSet();
        Instances train3_128 = source3_128.getDataSet();
        Instances train4_128 = source4_128.getDataSet();
        Instances train5_128 = source5_128.getDataSet();
        Instances train6_128 = source6_128.getDataSet();
        Instances train7_128 = source7_128.getDataSet();
        Instances train8_128 = source8_128.getDataSet();
        Instances train9_128 = source9_128.getDataSet();
        Instances train10_128 = source10_128.getDataSet();

        Instances train1_256 = source1_256.getDataSet();
        Instances train2_256 = source2_256.getDataSet();
        Instances train3_256 = source3_256.getDataSet();
        Instances train4_256 = source4_256.getDataSet();
        Instances train5_256 = source5_256.getDataSet();
        Instances train6_256 = source6_256.getDataSet();
        Instances train7_256 = source7_256.getDataSet();
        Instances train8_256 = source8_256.getDataSet();
        Instances train9_256 = source9_256.getDataSet();
        Instances train10_256 = source10_256.getDataSet();

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

        if (train7_64.classIndex() == -1) {
            train7_64.setClassIndex(train7_64.numAttributes() - 1);
        }
        if (train7_128.classIndex() == -1) {
            train7_128.setClassIndex(train7_128.numAttributes() - 1);
        }
        if (train7_256.classIndex() == -1) {
            train7_256.setClassIndex(train7_256.numAttributes() - 1);
        }

        if (train8_64.classIndex() == -1) {
            train8_64.setClassIndex(train8_64.numAttributes() - 1);
        }
        if (train8_128.classIndex() == -1) {
            train8_128.setClassIndex(train8_128.numAttributes() - 1);
        }
        if (train8_256.classIndex() == -1) {
            train8_256.setClassIndex(train8_256.numAttributes() - 1);
        }

        if (train9_64.classIndex() == -1) {
            train9_64.setClassIndex(train9_64.numAttributes() - 1);
        }
        if (train9_128.classIndex() == -1) {
            train9_128.setClassIndex(train9_128.numAttributes() - 1);
        }
        if (train9_256.classIndex() == -1) {
            train9_256.setClassIndex(train9_256.numAttributes() - 1);
        }

        if (train10_64.classIndex() == -1) {
            train10_64.setClassIndex(train10_64.numAttributes() - 1);
        }
        if (train10_128.classIndex() == -1) {
            train10_128.setClassIndex(train10_128.numAttributes() - 1);
        }
        if (train10_256.classIndex() == -1) {
            train10_256.setClassIndex(train10_256.numAttributes() - 1);
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

        List<Double> time_7_64 = new ArrayList<>();
        List<Double> time_7_128 = new ArrayList<>();
        List<Double> time_7_256 = new ArrayList<>();

        List<Double> time_8_64 = new ArrayList<>();
        List<Double> time_8_128 = new ArrayList<>();
        List<Double> time_8_256 = new ArrayList<>();

        List<Double> time_9_64 = new ArrayList<>();
        List<Double> time_9_128 = new ArrayList<>();
        List<Double> time_9_256 = new ArrayList<>();

        List<Double> time_10_64 = new ArrayList<>();
        List<Double> time_10_128 = new ArrayList<>();
        List<Double> time_10_256 = new ArrayList<>();

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

            lStartTime = System.nanoTime();
            label = cls7_J48_64.classifyInstance(train7_64.instance(i));
            lEndTime = System.nanoTime();
            res = lEndTime - lStartTime;
            time_7_64.add(res);
            lStartTime = System.nanoTime();
            label = cls7_J48_128.classifyInstance(train7_128.instance(i));
            lEndTime = System.nanoTime();
            res = lEndTime - lStartTime;
            time_7_128.add(res);
            lStartTime = System.nanoTime();
            label = cls7_J48_256.classifyInstance(train7_256.instance(i));
            lEndTime = System.nanoTime();
            res = lEndTime - lStartTime;
            time_7_256.add(res);

            lStartTime = System.nanoTime();
            label = cls8_J48_64.classifyInstance(train8_64.instance(i));
            lEndTime = System.nanoTime();
            res = lEndTime - lStartTime;
            time_8_64.add(res);
            lStartTime = System.nanoTime();
            label = cls8_J48_128.classifyInstance(train8_128.instance(i));
            lEndTime = System.nanoTime();
            res = lEndTime - lStartTime;
            time_8_128.add(res);
            lStartTime = System.nanoTime();
            label = cls8_J48_256.classifyInstance(train8_256.instance(i));
            lEndTime = System.nanoTime();
            res = lEndTime - lStartTime;
            time_8_256.add(res);

            lStartTime = System.nanoTime();
            label = cls9_J48_64.classifyInstance(train9_64.instance(i));
            lEndTime = System.nanoTime();
            res = lEndTime - lStartTime;
            time_9_64.add(res);
            lStartTime = System.nanoTime();
            label = cls9_J48_128.classifyInstance(train9_128.instance(i));
            lEndTime = System.nanoTime();
            res = lEndTime - lStartTime;
            time_9_128.add(res);
            lStartTime = System.nanoTime();
            label = cls9_J48_256.classifyInstance(train9_256.instance(i));
            lEndTime = System.nanoTime();
            res = lEndTime - lStartTime;
            time_9_256.add(res);

            lStartTime = System.nanoTime();
            label = cls10_J48_64.classifyInstance(train10_64.instance(i));
            lEndTime = System.nanoTime();
            res = lEndTime - lStartTime;
            time_10_64.add(res);
            lStartTime = System.nanoTime();
            label = cls10_J48_128.classifyInstance(train10_128.instance(i));
            lEndTime = System.nanoTime();
            res = lEndTime - lStartTime;
            time_10_128.add(res);
            lStartTime = System.nanoTime();
            label = cls10_J48_256.classifyInstance(train10_256.instance(i));
            lEndTime = System.nanoTime();
            res = lEndTime - lStartTime;
            time_10_256.add(res);
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

        Collections.sort(time_7_64);
        Collections.sort(time_7_128);
        Collections.sort(time_7_256);

        Collections.sort(time_8_64);
        Collections.sort(time_8_128);
        Collections.sort(time_8_256);

        Collections.sort(time_9_64);
        Collections.sort(time_9_128);
        Collections.sort(time_9_256);

        Collections.sort(time_10_64);
        Collections.sort(time_10_128);
        Collections.sort(time_10_256);

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

        System.out.println("\nJ48;7;64");
        for (int i = 0; i < 1000; i++){
            System.out.print(time_7_64.get(i));
            System.out.print(", ");
        }
        System.out.println("\nJ48;7;128");
        for (int i = 0; i < 1000; i++){
            System.out.print(time_7_128.get(i));
            System.out.print(", ");
        }
        System.out.println("\nJ48;7;256");
        for (int i = 0; i < 1000; i++){
            System.out.print(time_7_256.get(i));
            System.out.print(", ");
        }

        System.out.println("\nJ48;8;64");
        for (int i = 0; i < 1000; i++){
            System.out.print(time_8_64.get(i));
            System.out.print(", ");
        }
        System.out.println("\nJ48;8;128");
        for (int i = 0; i < 1000; i++){
            System.out.print(time_8_128.get(i));
            System.out.print(", ");
        }
        System.out.println("\nJ48;8;256");
        for (int i = 0; i < 1000; i++){
            System.out.print(time_8_256.get(i));
            System.out.print(", ");
        }

        System.out.println("\nJ48;9;64");
        for (int i = 0; i < 1000; i++){
            System.out.print(time_9_64.get(i));
            System.out.print(", ");
        }
        System.out.println("\nJ48;9;128");
        for (int i = 0; i < 1000; i++){
            System.out.print(time_9_128.get(i));
            System.out.print(", ");
        }
        System.out.println("\nJ48;9;256");
        for (int i = 0; i < 1000; i++){
            System.out.print(time_9_256.get(i));
            System.out.print(", ");
        }

        System.out.println("\nJ48;10;64");
        for (int i = 0; i < 1000; i++){
            System.out.print(time_10_64.get(i));
            System.out.print(", ");
        }
        System.out.println("\nJ48;10;128");
        for (int i = 0; i < 1000; i++){
            System.out.print(time_10_128.get(i));
            System.out.print(", ");
        }
        System.out.println("\nJ48;10;256");
        for (int i = 0; i < 1000; i++){
            System.out.print(time_10_256.get(i));
            System.out.print(", ");
        }
    }
}
