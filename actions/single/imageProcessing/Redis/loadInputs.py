#!/usr/bin/python 

import base64
import redis 
import sys  

if len(sys.argv) < 2:
    print('Please provide the Redis Endpoint\n')
    print('Example: ./loadInputs.py http://192.168.0.68')
    sys.exit(2)

TARGET_SIZE="1KB 16KB 32KB 64KB 126KB 257KB 517KB 1.3MB 2MB 3.2MB"

r = redis.StrictRedis(host=sys.argv[1], port='6379')
to_persist_redis = [
        {
            "key" : "1KB.jpg",
            "image" : "1KB.jpg"
        },
        {
            "key" : "16KB.jpg",
            "image" : "16KB.jpg"
        },
        {
            "key" : "32KB.jpg",
            "image" : "32KB.jpg"
        },
        {
            "key" : "64KB.jpg",
            "image" : "64KB.jpg"
        },
        {
            "key" : "126KB.jpg",
            "image" : "126KB.jpg"
        },
        {
            "key" : "257KB.jpg",
            "image" : "257KB.jpg"
        },
        {
            "key" : "517KB.jpg",
            "image" : "517KB.jpg"
        },
        {
            "key" : "1.3MB.jpg",
            "image" : "1.3MB.jpg"
        },
        {
            "key" : "2MB.jpg",
            "image" : "2MB.jpg"
        },
        {
            "key" : "3.2MB.jpg",
            "image" : "3.2MB.jpg"
        }
    ]

for elt in to_persist_redis:
    with open("../imgs/"+elt["image"],'rb') as imageFile:
        r.set(elt["key"],base64.b64encode(imageFile.read()))