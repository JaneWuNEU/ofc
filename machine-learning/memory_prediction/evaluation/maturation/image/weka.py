import os
import sys

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

FLAGS = ' --add-opens java.base/java.lang=ALL-UNNAMED -cp ' + WEKA_ABS_JAR_PAT  #first flags for delete warning and the second for weka

PATH = "../data_image/arff/"  #FOROTHERSFUNCTIONS path for arff file

PATH_RESULT = "../data_image/res/"  #FOROTHERSFUNCTIONS path for files generate by weka included tests files
os.makedirs(PATH_RESULT, exist_ok=True)

for fct in range(1, 11):
    for nb_cluster in [128]:  #, 128, 256]:
        name_fonction = "function" + str(fct)
        print("===", name_fonction, "===")
        print("\n==J48==\n")
        for nb_donne in [
                10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90,
                100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700,
                750, 800, 850, 900, 950, 1000
        ]:
            Algo = 'J48'

            trainfile = PATH + name_fonction + '_train_' + str(nb_donne) + '.arff'
            testfile = PATH + name_fonction + '_test' + '.arff'

            print("\nTrain for k=" + str(nb_donne) + " with " + str(Algo) +
                  "\nWait ;)")
            os.system('java' + FLAGS + space + model_tree + Algo + space + '-t ' +
                      trainfile + ' -U -d ' + PATH_RESULT + name_fonction +
                      '_output_model.model > ' + PATH_RESULT + name_fonction +
                      '_model_learn_stats_' + Algo + '_' + str(nb_donne) + '.txt')
            print("Produce classified outputs...")
            os.system('java' + FLAGS + space + model_tree + Algo + ' -l ' +
                      PATH_RESULT + name_fonction + '_output_model.model -T ' +
                      testfile + ' -p 0 > ' + PATH_RESULT + name_fonction +
                      '_output_' + Algo + '_' + str(nb_donne) + csv)
            print("Produce tester stats")
            os.system('java' + FLAGS + space + model_tree + Algo + ' -l ' +
                      PATH_RESULT + name_fonction + '_output_model.model -T ' +
                      testfile + ' > ' + PATH_RESULT + name_fonction +
                      '_model_test_stats_' + Algo + '_' + str(nb_donne) + '.csv')
