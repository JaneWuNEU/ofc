"""
This file print the result of each decision tree for each function.
It search the informations in the weka file create with weka.py
"""

FUNCTION_IDS = [1, 2, 3, 4, 5, 6]
NBS_CLUSTERS = [64, 128, 256]
ALGORITHMS = ['J48', 'RandomTree', 'RandomForest', 'HoeffdingTree']


def print_prediction_tests():
    print("algorithm;function_id;clusters;truth;prediction")

    for fct in FUNCTION_IDS:
        for nb_cluster in NBS_CLUSTERS:
            for name_fct in ALGORITHMS:
                with open(
                        "../res/function" + str(fct) + "_" + str(nb_cluster) +
                        "_output_" + name_fct + "_10.csv", "r") as pred_infile:
                    _print_prediction_tests(fct, nb_cluster, name_fct, pred_infile)


def _print_prediction_tests(func_id, nb_clusters, algorithm, infile):
    line = next(infile)
    while "inst#" not in line:
        line = next(infile)

    for line in infile:
        line = line.rstrip()
        if not line:
            continue

        value = ''
        predicted = ''
        # search the true value
        index1 = line.index("x")
        value += line[index1 + 1]
        if line[index1 + 2] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            value += line[index1 + 2]
        value = int(value)
        line = line[index1 + 1:]
        # search the predicted value
        index2 = line.index("x")
        predicted += line[index2 + 1]
        if line[index2 + 2] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            predicted += line[index2 + 2]
        predicted = int(predicted)

        sep = ";"
        print(algorithm + sep + str(func_id) + sep + str(nb_clusters) + sep +
              str(value) + sep + str(predicted))


if __name__ == '__main__':
    print_prediction_tests()
