import math
import os
""" This file create an arff file for each function """

dic = {}
nb_cluster = 2

os.makedirs("arff", exist_ok=True)

#   we extract the features from a csv file
res = open("../../data/features_image.csv", "r")
first = True
for line in res:
    if first:
        first = False
    else:
        url, file_size, sizex, sizey = line[:-1].split(";")
        url = url.split("/")[-1]
        dic[url] = [str(file_size), str(sizex), str(sizey)]
res.close()

for fct in range(1, 11):

    name = "function" + str(fct)
    file = open("csv/" + name + ".csv", "r")
    res = open("arff/" + name + ".arff", "w")

    # csv is an array with the data of the csv file, without the header
    csv = list(map(lambda x: x[:-1].split(";"), file.readlines()))[1:]

    if fct == 1:
        nb_argument = 2
    elif fct in [3, 4, 6, 8, 9, 10]:
        nb_argument = 1
    else:
        nb_argument = 0

    # we create the header of the arff file
    res.write(
        "% 1. Title: Function1 Python\n%\n% 2. Sources:\n%      Creator: Stephane Pouget\n%      Date: May, 2020\n%\n@RELATION "
        + name + "\n")

    res.write("@ATTRIBUTE input_size   NUMERIC\n")
    res.write("@ATTRIBUTE sizex   NUMERIC\n")
    res.write("@ATTRIBUTE sizey   NUMERIC\n")

    for k in range(nb_argument):
        if fct == 9:
            res.write("@ATTRIBUTE arguments1   {png, webp, tiff, jpg}\n")
        else:
            res.write("@ATTRIBUTE arguments" + str(k + 1) + "   NUMERIC\n")

    res.write("@ATTRIBUTE cache       {")
    for k in range(nb_cluster):
        res.write("x" + str(k) + ",")
    res.write("}\n")

    res.write("@DATA\n")

    # we add the data for the arff file
    for k in range(len(csv)):
        line = csv[k]
        input_size = line[3]
        url = line[2]
        loading_input_time = float(line[4])
        processing_time = float(line[5])
        loading_result_time = float(line[6])

        if nb_argument == 0:
            arguments = []
        if nb_argument == 1:
            arguments = [line[-1]]
        if nb_argument == 2:
            arguments = [line[-2], line[-1]]

        file_size, sizex, sizey = dic[url]

        l = [file_size, sizex, sizey]

        if "nan" in l:
            continue

        for i in range(len(arguments)):
            l += [arguments[i]]

        # we search the cluster of the cache
        if (loading_result_time + loading_input_time) / (
                loading_result_time + loading_input_time + processing_time) > 0.5:
            cluster = "x1"
        else:
            cluster = "x0"
        l += [cluster]

        res.write(",".join(l) + "\n")

    file.close()
    res.close()
