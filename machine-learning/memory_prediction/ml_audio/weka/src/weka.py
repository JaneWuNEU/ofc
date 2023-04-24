import os
import sys
"""
This file creates models and do test for each function with decision tree
I use cross validation to avoid overfitting
"""

try:
    WEKA_ABS_JAR_PAT = os.environ['WEKA_JAR']
    if not WEKA_ABS_JAR_PAT:
        raise KeyError
except KeyError:
    print('Environment variable "WEKA_JAR" unset or empty', file=sys.stderr)
    sys.exit(2)

space = ' '

model_SRF = 'weka.filters.supervised.instance.StratifiedRemoveFolds'
model_tree = 'weka.classifiers.trees.'
csv = '.csv'

os.makedirs("../res", exist_ok=True)

for fct in range(1, 7):
    for nb_cluster in [64, 128, 256]:
        name_function = "function" + str(fct) + "_" + str(nb_cluster)
        print("===", name_function, "===")
        name_file = "../../../data_audio/arff/" + name_function + ".arff"

        FLAGS = ' --add-opens java.base/java.lang=ALL-UNNAMED -cp ' + WEKA_ABS_JAR_PAT  #first flags for delete warning and the second for weka

        # cross validation with different partitioning
        for k in [3, 5, 10]:
            os.system('java' + FLAGS + space + model_SRF + space + '-i' + space +
                      '../res/' + name_file + ' -o ../res/' + name_function +
                      '_metric-train_' + str(k) + '.arff -c last -N' + space +
                      str(k) + space + '-F 1 -V -S 42')
            os.system('java' + FLAGS + space + model_SRF + space + '-i' + space +
                      '../res/' + name_file + ' -o ../res/' + name_function +
                      '_metric-test_' + str(k) + '.arff -c last -N' + space +
                      str(k) + space + '-F 1 -S 42')

        # generation of model and result for J48
        print("\n==J48==\n")
        for k in [3, 5, 10]:  #juste for J48 because it's different option
            Algo = 'J48'
            trainfile = '../res/' + name_function + '_metric-train_' + str(
                k) + '.arff'
            testfile = '../res/' + name_function + '_metric-test_' + str(
                k) + '.arff'
            print("\nTrain for k=" + str(k) + " with " + str(Algo) + "\nWait ;)")
            os.system('java' + FLAGS + space + model_tree + Algo + space + '-t ' +
                      trainfile + ' -d ../res/' + name_function + '_output_model_' +
                      str(Algo) + '_' + str(nb_cluster) + '.model > ../res/' +
                      name_function + '_model_learn_stats_' + Algo + '_' + str(k) +
                      '.txt')
            print("Produce classified outputs...")
            os.system('java' + FLAGS + space + model_tree + Algo + ' -l ../res/' +
                      name_function + '_output_model_' + str(Algo) + '_' +
                      str(nb_cluster) + '.model -T ' + testfile + ' -p 0 > ' +
                      '../res/' + name_function + '_output_' + Algo + '_' + str(k) +
                      csv)
            print("Produce tester stats")
            os.system('java' + FLAGS + space + model_tree + Algo + ' -l ../res/' +
                      name_function + '_output_model_' + str(Algo) + '_' +
                      str(nb_cluster) + '.model -T ' + testfile + ' > ' +
                      '../res/' + name_function + '_model_test_stats_' + Algo +
                      '_' + str(k) + '.csv')

        # generation of model and result for RandomTree, RandomForest, HoeffdingTree
        for Algo in ['RandomTree', 'RandomForest', 'HoeffdingTree']:
            print("\n==" + Algo + "==\n")
            for k in [3, 5, 10]:
                trainfile = '../res/' + name_function + '_metric-train_' + str(
                    k) + '.arff'
                testfile = '../res/' + name_function + '_metric-test_' + str(
                    k) + '.arff'
                print("\nTrain for k=" + str(k) + " with " + str(Algo) +
                      "\nWait ;)")
                os.system('java' + FLAGS + space + model_tree + Algo + space +
                          ' -M 5 -N 5 -t ' + trainfile + ' -d ../res/' +
                          name_function + '_output_model_' + str(Algo) + '_' +
                          str(nb_cluster) + '.model > ../res/' + name_function +
                          '_model_learn_stats_' + Algo + '_' + str(k) + '.txt')
                print("Produce classified outputs...")
                os.system('java' + FLAGS + space + model_tree + Algo +
                          ' -l ../res/' + name_function + '_output_model_' +
                          str(Algo) + '_' + str(nb_cluster) + '.model -T ' +
                          testfile + ' -p 0 > ' + '../res/' + name_function +
                          '_output_' + Algo + '_' + str(k) + csv)
                print("Produce tester stats")
                os.system('java' + FLAGS + space + model_tree + Algo +
                          ' -l ../res/' + name_function + '_output_model_' +
                          str(Algo) + '_' + str(nb_cluster) + '.model -T ' +
                          testfile + ' > ' + '../res/' + name_function +
                          '_model_test_stats_' + Algo + '_' + str(k) + '.csv')
