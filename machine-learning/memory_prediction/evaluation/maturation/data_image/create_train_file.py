import os
import random

os.makedirs("arff", exist_ok=True)

for fct in range(1, 11):
    name_fct = "function" + str(fct)

    train_file = name_fct + "_train_"
    test_file = name_fct + "_test.arff"

    #FOROTHERSFUNCTIONS change this path to have the original arff
    file = open("../../../data_image/arff/function" + str(fct) + "_128.arff", "r")

    first = True

    data = []

    for line in file:
        if first:
            if "@DATA" in line:
                first = False
        else:
            l = line[:-1].split(",")
            data += [l]
    file.close()
    possibilite = [i for i in range(len(data))]
    test = []
    train = []

    for i in range(700):  # the number of data in the test file
        x = random.randint(0, len(possibilite) - 1)
        test += [x]
        del possibilite[x]

    for i in range(1000):  # the number of data for the train file
        x = random.randint(0, len(possibilite) - 1)
        train += [x]
        del possibilite[x]

    file = open("arff/" + test_file, "w")

    #FOROTHERSFUNCTIONS headers of the ARFF file, change this for other functions
    file.write("@RELATION fct" + str(fct) + "\n")
    file.write("@ATTRIBUTE input_size   NUMERIC\n")
    file.write("@ATTRIBUTE sizeX   NUMERIC\n")
    file.write("@ATTRIBUTE sizeY   NUMERIC\n")
    if fct == 6:
        file.write("@ATTRIBUTE arguments1   NUMERIC\n")
        file.write("@ATTRIBUTE arguments2   NUMERIC\n")
    if fct in [1, 3, 5, 8, 9]:
        file.write("@ATTRIBUTE arguments1   NUMERIC\n")
    if fct == 4:
        file.write("@ATTRIBUTE arguments1   {png, webp, tiff, jpg}\n")

    file.write(
        "@ATTRIBUTE memory       {x0,x1,x2,x3,x4,x5,x6,x7,x8,x9,x10,x11,x12,x13,x14,x15,x16,x17,x18,x19,x20,x21,x22,x23,x24,x25,x26,x27,x28,x29,x30,x31,x32,x33,x34,x35,x36,x37,x38,x39,x40,x41,x42,x43,x44,x45,x46,x47,x48,x49,x50,x51,x52,x53,x54,x55,x56,x57,x58,x59,x60,x61,x62,x63,x64,x65,x66,x67,x68,x69,x70,x71,x72,x73,x74,x75,x76,x77,x78,x79,x80,x81,x82,x83,x84,x85,x86,x87,x88,x89,x90,x91,x92,x93,x94,x95,x96,x97,x98,x99,x100,x101,x102,x103,x104,x105,x106,x107,x108,x109,x110,x111,x112,x113,x114,x115,x116,x117,x118,x119,x120,x121,x122,x123,x124,x125,x126,x127}\n"
    )
    file.write("@DATA\n")
    for i in range(len(test)):
        d = data[test[i]]
        file.write(",".join(d) + "\n")

    file.close()

    for id in [
            10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 100,
            150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800,
            850, 900, 950, 1000
    ]:
        file = open("arff/" + train_file + str(id) + ".arff", "w")

        #FOROTHERSFUNCTIONS headers of the ARFF file, change this for other functions
        file.write("@RELATION fct" + str(fct) + "\n")
        file.write("@ATTRIBUTE input_size   NUMERIC\n")
        file.write("@ATTRIBUTE sizeX   NUMERIC\n")
        file.write("@ATTRIBUTE sizeY   NUMERIC\n")
        if fct == 6:
            file.write("@ATTRIBUTE arguments1   NUMERIC\n")
            file.write("@ATTRIBUTE arguments2   NUMERIC\n")
        if fct in [1, 3, 5, 8, 9]:
            file.write("@ATTRIBUTE arguments1   NUMERIC\n")
        if fct == 4:
            file.write("@ATTRIBUTE arguments1   {png, webp, tiff, jpg}\n")

        file.write(
            "@ATTRIBUTE memory       {x0,x1,x2,x3,x4,x5,x6,x7,x8,x9,x10,x11,x12,x13,x14,x15,x16,x17,x18,x19,x20,x21,x22,x23,x24,x25,x26,x27,x28,x29,x30,x31,x32,x33,x34,x35,x36,x37,x38,x39,x40,x41,x42,x43,x44,x45,x46,x47,x48,x49,x50,x51,x52,x53,x54,x55,x56,x57,x58,x59,x60,x61,x62,x63,x64,x65,x66,x67,x68,x69,x70,x71,x72,x73,x74,x75,x76,x77,x78,x79,x80,x81,x82,x83,x84,x85,x86,x87,x88,x89,x90,x91,x92,x93,x94,x95,x96,x97,x98,x99,x100,x101,x102,x103,x104,x105,x106,x107,x108,x109,x110,x111,x112,x113,x114,x115,x116,x117,x118,x119,x120,x121,x122,x123,x124,x125,x126,x127}\n"
        )
        file.write("@DATA\n")
        for i in range(id):
            d = data[train[i]]
            file.write(",".join(d) + "\n")
        file.close()
