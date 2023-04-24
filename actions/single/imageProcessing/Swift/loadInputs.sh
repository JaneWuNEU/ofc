#!/bin/bash

workdir=$(pwd)
if which swift >/dev/null; then echo ""
else
    sudo apt update 
    sudo apt install python3-pip
    sudo pip3 install python-swiftclient 
fi 
# Repackage the functions 

if [ -z $1 ]; then
    echo "Please provide @SWIFT_END_POINT as parameter.\n"
    echo "Usage: $0 @SWIFT_END_POINT\n"
    echo "Example: $0 http://192.168.0.148\n"
fi 


# Import images
cd $workdir/../imgs/
TARGET_SIZE="1 16 32 64 126 256 512 1024 2048 3072 4096"

echo "Creating swift user test with password tester"
swift -A http://127.0.0.1:8080/auth/v1.0 -U test:tester -K testing post expe-faas

for target in $TARGET_SIZE; do
    #wget https://expe-faas.s3.amazonaws.com/$target.avi
    echo "Putting $target.jpg to swift. Sending curl request" 
    swift -A http://127.0.0.1:8080/auth/v1.0 -U test:tester -K testing upload --object-name $target.jpg expe-faas $target.jpg
    rm $target.jpg 
done

cd $workdir

