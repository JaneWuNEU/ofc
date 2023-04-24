"""
Simple script to extract data from general csv in order to generate a csv by function
"""

import os

#input file with all data
file = open("../../data/data_image_memory.csv", "r")

#output files with data for each function
os.makedirs("csv", exist_ok=True)
f1 = open("csv/function1.csv", "w")
f2 = open("csv/function2.csv", "w")
f3 = open("csv/function3.csv", "w")
f4 = open("csv/function4.csv", "w")
f5 = open("csv/function5.csv", "w")
f6 = open("csv/function6.csv", "w")
f7 = open("csv/function7.csv", "w")
f8 = open("csv/function8.csv", "w")
f9 = open("csv/function9.csv", "w")
f10 = open("csv/function10.csv", "w")

dic6 = {}

csv = file.readlines()  #csv is an array with all data from file
header = csv[0]  # the header is the first element
csv = csv[1:]  # we delete the header

f1.write("function;id;url;image_size;truth_memory;sigma\n")
f2.write("function;id;url;image_size;truth_memory\n")

f3.write("function;id;url;image_size;truth_memory;width\n")
f4.write("function;id;url;image_size;truth_memory;format\n")

f5.write("function;id;url;image_size;truth_memory;sigma\n")
f6.write("function;id;url;image_size;truth_memory;threshold;softness\n")

f7.write("function;id;url;image_size;truth_memory\n")
f8.write("function;id;url;image_size;truth_memory;width\n")

f9.write("function;id;url;image_size;truth_memory;angle\n")
f10.write("function;id;url;image_size;truth_memory\n")
c = ";"
n = "\n"

# we extract according to the id of the function
for line in csv:
    fct, id, url, image_size, truth_memory, name, arguments, outputsize, init_ms, end_ms = line[:-1].split(
        ",")
    if int(fct) == 1:
        if name == "sigma":
            f1.write(fct + c + id + c + url + c + image_size + c + truth_memory +
                     c + arguments + n)
    if int(fct) == 2:
        f2.write(fct + c + id + c + url + c + image_size + c + truth_memory + n)
    if int(fct) == 3:
        if name == "width":
            f3.write(fct + c + id + c + url + c + image_size + c + truth_memory +
                     c + arguments + n)
    if int(fct) == 4:
        if name == "format":
            f4.write(fct + c + id + c + url + c + image_size + c + truth_memory +
                     c + arguments + n)
    if int(fct) == 5:
        if name == "sigma":
            f5.write(fct + c + id + c + url + c + image_size + c + truth_memory +
                     c + arguments + n)
    if int(fct) == 7:
        f7.write(fct + c + id + c + url + c + image_size + c + truth_memory + n)
    if int(fct) == 8:
        if name == "width":
            f8.write(fct + c + id + c + url + c + image_size + c + truth_memory +
                     c + arguments + n)
    if int(fct) == 9:
        if name == "angle":
            f9.write(fct + c + id + c + url + c + image_size + c + truth_memory +
                     c + arguments + n)
    if int(fct) == 10:
        f10.write(fct + c + id + c + url + c + image_size + c + truth_memory + n)
    if int(fct) == 6:
        if name != "url":
            if name == "softness":
                #i.e. it is the second arguments
                dic6[id][name] = arguments
                f6.write(fct + ";" + id + ";" + url + ";" + image_size + ";" +
                         truth_memory + ";" + dic6[id]["threshold"] + ";" +
                         dic6[id]["softness"] + "\n")

            if name == "threshold":
                dic6[id] = {}
                dic6[id][name] = arguments

f1.close()
f2.close()
f3.close()
f4.close()
f5.close()
f6.close()
f7.close()
f8.close()
f9.close()
f10.close()
file.close()
