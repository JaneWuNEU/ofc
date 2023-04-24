import math
import os
""" This file create an arff file for each function """

dic = {}
nb_cluster = 2

os.makedirs("arff", exist_ok=True)

csv = open("../../data/features_audio.csv", "r")
for line in csv:
    l = line[:-1].split(";")
    dic[l[0].split("/")[-1]] = l[1:]
csv.close()

for fct in range(1, 7):

    name = "function" + str(fct)
    file = open("csv/" + name + ".csv", "r")
    res = open("arff/" + name + ".arff", "w")

    # csv is an array with the data of the csv file, without the header
    csv = list(map(lambda x: x[:-1].split(";"), file.readlines()))[1:]

    if fct == 1:
        nb_argument = 1
    else:
        nb_argument = 0

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
        # truth_memory = line[4]
        loading_input_time = float(line[4])  # e in etl
        processing_time = float(line[5])  # t in etl
        loading_result_time = float(line[6])  # l in etl

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
