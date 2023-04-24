import sys
"""
This file print the result of each decision tree for each function.
It search the informations in the weka file create with weka.py
"""

#print the header
print("algorithm;function_id;clusters;pred_exact;pred_above")
for fct in range(1, 11):
    id = 1
    for nb_cluster in [64, 128, 256]:
        for name_fct in ['J48', 'RandomTree', 'RandomForest', 'HoeffdingTree']:

            file = open(
                "../res/function" + str(fct) + "_" + str(nb_cluster) + "_output_" +
                name_fct + "_10.csv", "r")
            data = list(map(lambda x: x[:-1], file.readlines()))

            while "" in data:
                data.remove("")

            first = True  # to avoid header
            good_prediction = 0  # when prediction >= true value
            good_prediction2 = 0  # when true value + 2 >= prediction >= true value
            good_prediction3 = 0  # when prediction == true value
            counter = 0
            for k in range(len(data)):
                line = data[k]
                value = ''
                predicted = ''
                if first:  # to avoid header
                    if "inst#" in line:
                        first = False
                else:
                    counter += 1
                    # search the true value
                    index1 = line.index("x")
                    value += line[index1 + 1]
                    if line[index1 + 2] in [
                            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'
                    ]:
                        value += line[index1 + 2]
                    value = int(value)
                    line = line[index1 + 1:]
                    # search the predicted value
                    index2 = line.index("x")
                    predicted += line[index2 + 1]
                    if line[index2 + 2] in [
                            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'
                    ]:
                        predicted += line[index2 + 2]
                    predicted = int(predicted)

                    if int(value) <= int(predicted):
                        good_prediction += 1
                        if predicted - value <= 2:
                            good_prediction2 += 1
                            if predicted == value:
                                good_prediction3 += 1

            c = ";"
            print(name_fct + c + str(fct) + c + str(nb_cluster) + c +
                  str(good_prediction3 / counter * 100) + c +
                  str(good_prediction / counter * 100))

            file.close()
