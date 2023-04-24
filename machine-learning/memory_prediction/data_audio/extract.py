"""
Simple script to extract data from general csv in order to generate a csv by function
"""

import os

#input file with all data
file = open("../../data/data_audio_memory.csv", "r")

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
csv = csv[1:]  # we delete the header

#headers
f1.write("function;id;url;image_size;truth_memory;format\n")
f2.write("function;id;url;image_size;truth_memory\n")

f3.write("function;id;url;image_size;truth_memory\n")
f4.write("function;id;url;image_size;truth_memory\n")

f5.write("function;id;url;image_size;truth_memory\n")
f6.write("function;id;url;image_size;truth_memory\n")

c = ";"
n = "\n"

# we extract according to the id of the function
for line in csv:
    fct, id, url, image_size, truth_memory, name, arguments, outputsize, start_ms, end_ms = line[:-1].split(
        ",")
    if int(outputsize) != 0:
        if int(fct) == 1:
            if name == "format":
                f1.write(fct + c + id + c + url + c + image_size + c +
                         truth_memory + c + arguments + n)
        if int(fct) == 2:
            f2.write(fct + c + id + c + url + c + image_size + c + truth_memory + n)
        if int(fct) == 3:
            f3.write(fct + c + id + c + url + c + image_size + c + truth_memory + n)
        if int(fct) == 4:
            f4.write(fct + c + id + c + url + c + image_size + c + truth_memory + n)
        if int(fct) == 5:
            f5.write(fct + c + id + c + url + c + image_size + c + truth_memory + n)
        if int(fct) == 6:
            f6.write(fct + c + id + c + url + c + image_size + c + truth_memory + n)

f1.close()
f2.close()
f3.close()
f4.close()
f5.close()
f6.close()

file.close()
