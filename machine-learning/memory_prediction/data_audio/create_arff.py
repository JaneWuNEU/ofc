import math
import os
""" This file create an arff file for each function, it use a csv file create with features.py """


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


dic = {}

csv = open("../../data/features_audio.csv", "r")
for line in csv:
    l = line[:-1].split(";")
    dic[l[0]] = l[1:]
csv.close()

# size of the memory interval i.e. [0, 2048] MB
mini = 0
maxi = 2048000000

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

    for fct in range(1, 7):

        name = "function" + str(fct)
        file = open("csv/" + name + ".csv", "r")
        res = open("arff/" + name + "_" + str(nb_cluster) + ".arff", "w")

        # csv is an array with the data of the csv file, without the header
        csv = list(map(lambda x: x[:-1].split(";"), file.readlines()))[1:]

        nb_argument = len(csv[0]) - 5

        # we create the header of the arff file
        res.write(
            "% 1. Title: Function1 Python\n%\n% 2. Sources:\n%      Creator: Stephane Pouget\n%      Date: May, 2020\n%\n@RELATION "
            + name + "\n")

        res.write("@ATTRIBUTE input_size   NUMERIC\n")
        res.write("@ATTRIBUTE duration   NUMERIC\n")
        res.write("@ATTRIBUTE frames   NUMERIC\n")

        for k in range(nb_argument):
            if fct == 1:
                res.write("@ATTRIBUTE arguments1   {mp3, wav, aiff}\n")
            else:
                res.write("@ATTRIBUTE arguments" + str(k + 1) + "   NUMERIC\n")

        res.write("@ATTRIBUTE memory       {")
        for k in range(nb_cluster):
            res.write("x" + str(k) + ",")
        res.write("}\n")

        res.write("@DATA\n")

        # we add the data for the arff file
        for k in range(len(csv)):
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

            _, samplerate, channels, duration, frames, length = dic[url]

            l = [input_size, duration, frames]

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

        #print the clusters actually used
        s = ""
        for w in range(nb_cluster):
            if real_interval[w] != 0:
                s += "x" + str(w) + ","
        file.close()
        res.close()
