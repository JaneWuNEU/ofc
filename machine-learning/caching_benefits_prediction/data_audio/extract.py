"""
Simple script to extract data from general csv in order to generate a csv by function
"""
import os

import numpy as np

dic = {}


def mean(l):
    res = []
    for k in range(len(l)):
        function, id, multiruns_ID, url, image_size, truth_memory, name, arguments, outputsize, init_ms, end_ms, loading_input_time, processing_time, loading_result_time = l[
            k][:-1].split(",")
        try:
            if function == "1":
                if name == "format":
                    dic[multiruns_ID] += [[
                        function, id, multiruns_ID, url, image_size, truth_memory,
                        name, arguments, outputsize, init_ms, end_ms,
                        loading_input_time, processing_time, loading_result_time
                    ]]
            else:
                dic[multiruns_ID] += [[
                    function, id, multiruns_ID, url, image_size, truth_memory, name,
                    arguments, outputsize, init_ms, end_ms, loading_input_time,
                    processing_time, loading_result_time
                ]]
        except:
            dic[multiruns_ID] = []
            if function == "1":
                if name == "format":
                    dic[multiruns_ID] += [[
                        function, id, multiruns_ID, url, image_size, truth_memory,
                        name, arguments, outputsize, init_ms, end_ms,
                        loading_input_time, processing_time, loading_result_time
                    ]]
            else:
                dic[multiruns_ID] += [[
                    function, id, multiruns_ID, url, image_size, truth_memory, name,
                    arguments, outputsize, init_ms, end_ms, loading_input_time,
                    processing_time, loading_result_time
                ]]
    for key in dic:
        if len(dic[key]) == 10:
            d = dic[key]
            input = []
            calculation = []
            output = []

            for i in range(10):
                d[i][-3] = float(d[i][-3])
                d[i][-2] = float(d[i][-2])
                d[i][-1] = float(d[i][-1])
                input += [d[i][-3]]
                calculation += [d[i][-2]]
                output += [d[i][-1]]
            s = set()
            s.add(np.argmax(input))
            s.add(np.argmin(input))
            s.add(np.argmax(calculation))
            s.add(np.argmin(calculation))
            s.add(np.argmax(output))
            s.add(np.argmin(output))
            j = 0
            for i in s:
                del d[i - j]
                j += 1
            input = 0
            calculation = 0
            output = 0
            for i in range(len(d)):
                input += d[i][-3]
                calculation += d[i][-2]
                output += d[i][-1]
            input /= len(d)
            calculation /= len(d)
            output /= len(d)
            d[0][-3] = input
            d[0][-2] = calculation
            d[0][-1] = output
            res += [d[0]]

    return res


#input file with all data
file = open("../../data/data_audio_caching.csv", "r")

#output files with data for each function
os.makedirs("csv", exist_ok=True)
f1 = open("csv/function1.csv", "w")
f2 = open("csv/function2.csv", "w")
f3 = open("csv/function3.csv", "w")
f4 = open("csv/function4.csv", "w")
f5 = open("csv/function5.csv", "w")
f6 = open("csv/function6.csv", "w")

csv = file.readlines()  #csv is an array with all data from file
header = csv[0]  # the header is the first element
csv = mean(csv[1:])  # we delete the header

#headers
f1.write(
    "function;id;url;image_size;loading_input_time;processing_time;loading_result_time;truth_memory;format\n"
)
f2.write(
    "function;id;url;image_size;loading_input_time;processing_time;loading_result_time;truth_memory\n"
)

f3.write(
    "function;id;url;image_size;loading_input_time;processing_time;loading_result_time;truth_memory\n"
)
f4.write(
    "function;id;url;image_size;loading_input_time;processing_time;loading_result_time;truth_memory\n"
)

f5.write(
    "function;id;url;image_size;loading_input_time;processing_time;loading_result_time;truth_memory\n"
)
f6.write(
    "function;id;url;image_size;loading_input_time;processing_time;loading_result_time;truth_memory\n"
)

c = ";"
n = "\n"

# we extract according to the id of the function
for line in csv:
    function, id, multiruns_ID, url, image_size, truth_memory, name, arguments, outputsize, init_ms, end_ms, loading_input_time, processing_time, loading_result_time = list(
        map(str, line))
    if int(outputsize) != 0:
        if int(function) == 1:
            if name == "format":
                f1.write(function + c + id + c + url + c + image_size + c +
                         loading_input_time + c + processing_time + c +
                         loading_result_time + c + truth_memory + c + arguments + n)
        if int(function) == 2:
            f2.write(function + c + id + c + url + c + image_size + c +
                     loading_input_time + c + processing_time + c +
                     loading_result_time + c + truth_memory + n)
        if int(function) == 3:
            f3.write(function + c + id + c + url + c + image_size + c +
                     loading_input_time + c + processing_time + c +
                     loading_result_time + c + truth_memory + n)
        if int(function) == 4:
            f4.write(function + c + id + c + url + c + image_size + c +
                     loading_input_time + c + processing_time + c +
                     loading_result_time + c + truth_memory + n)
        if int(function) == 5:
            f5.write(function + c + id + c + url + c + image_size + c +
                     loading_input_time + c + processing_time + c +
                     loading_result_time + c + truth_memory + n)
        if int(function) == 6:
            f6.write(function + c + id + c + url + c + image_size + c +
                     loading_input_time + c + processing_time + c +
                     loading_result_time + c + truth_memory + n)

f1.close()
f2.close()
f3.close()
f4.close()
f5.close()
f6.close()

file.close()
