""" This file create an arff file for each function, it use a csv file create with features.py """

import math
import os


def in_interval(value, interval):
    """ return a boolean to know if it is inside the interval """
    if value >= interval[0] and value <= interval[1]:
        return True
    else:
        return False


def search_interval(value, linterval):
    """ search the interval of the value """
    for k in range(len(linterval)):
        if in_interval(value, linterval[k]):
            return k


# size of the memory interval i.e. [0, 2048] MB
mini = 0
maxi = 2048000000

dic = {}

#   we extract the features from a csv file
res = open("../../data/features_image.csv", "r")
first = True
for line in res:
    if first:
        first = False
    else:
        url, file_size, sizex, sizey = line[:-1].split(";")
        dic[url] = [str(file_size), str(sizex), str(sizey)]
res.close()

os.makedirs("arff", exist_ok=True)

# we divide the memory interval in diffirent number of cluster
for nb_cluster in [64, 128, 256]:

    # size of the interval with nb_cluster
    size_interval = (maxi - mini) / nb_cluster

    # irray with the id of each cluster
    real_interval = [0 for i in range(nb_cluster)]

    # interval is a 2D array, each line represent one cluster
    # with the memory interval of this cluster
    interval = [[mini + i * size_interval, mini + (i + 1) * size_interval]
                for i in range(nb_cluster)]

    for fct in range(1, 11):
        name = "function" + str(fct)
        file = open("csv/" + name + ".csv", "r")
        res = open("arff/" + name + "_" + str(nb_cluster) + ".arff", "w")

        # csv is an array with the data of the csv file, without the header
        csv = list(map(lambda x: x[:-1].split(";"), file.readlines()))[1:]

        nb_argument = len(csv[0]) - 5

        # we create the header of the arff file
        res.write(
            "% 1. Title: Function" + str(fct) +
            " Python\n%\n% 2. Sources:\n%      Creator: Stephane Pouget\n%      Date: May, 2020\n%\n@RELATION "
            + name + "\n")

        res.write("@ATTRIBUTE input_size   NUMERIC\n")
        res.write("@ATTRIBUTE sizeX   NUMERIC\n")
        res.write("@ATTRIBUTE sizeY   NUMERIC\n")

        for k in range(nb_argument):
            if fct == 4:
                res.write("@ATTRIBUTE arguments" + str(k + 1) +
                          "   {png, webp, tiff, jpg}\n")
            else:
                res.write("@ATTRIBUTE arguments" + str(k + 1) + "   NUMERIC\n")

        res.write("@ATTRIBUTE memory       {")
        for k in range(nb_cluster):
            res.write("x" + str(k) + ",")
        res.write("}\n")

        res.write("@DATA\n")

        # we add the data for the arff file
        for k in range(len(csv)):
            try:
                line = csv[k]

                input_size = line[3]
                url = line[2]
                truth_memory = line[4]
                if nb_argument == 0:
                    arguments = []
                if nb_argument == 1:
                    arguments = [line[-1]]
                if nb_argument == 2:
                    arguments = [line[-2], line[-1]]

                _, sizex, sizey = dic[url]

                l = [input_size, sizex, sizey]

                if "nan" in l:
                    continue

                for i in range(len(arguments)):
                    l += [arguments[i]]

                # we search the cluster of the memory
                val_interval = search_interval(int(truth_memory), interval)
                real_interval[val_interval] += 1
                cluster = "x" + str(val_interval)
                l += [cluster]

                res.write(",".join(l) + "\n")
            except:
                continue

        #print the clusters actually used
        s = ""
        for w in range(nb_cluster):
            if real_interval[w] != 0:
                s += "x" + str(w) + ","
        file.close()
        res.close()
