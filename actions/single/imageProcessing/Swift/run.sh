#!/bin/bash 

func_names = ['wand_blur','wand_resize','wand_sepia','wand_rotate','wand_denoise','wand_edge','map_reduce','THIS']

# Wait period in seconds 
inter_func_wait=5

workdir=$(pwd)

# Repackage the functions 
build=true

if [ -z $1 ]; then
    echo "Please provide @SWIFT_END_POINT as parameter.\n"
    echo "Usage: $0 @SWIFT_END_POINT\n"
    echo "Example: $0 http://192.168.0.148\n"
fi 


if $build; then 
    docker build -t python3action:magick .
    docker run --rm -v "$PWD:/tmp" openwhisk/python3action bash \
             -c "cd tmp && virtualenv virtualenv && source virtualenv/bin/activate && pip install -r requirements.txt"

    for func in "${func_names[@]}"
    do 

        echo "Building $func directory"     

        rm -f $func.zip 
        zip -r $func.zip virtualenv; zip -j $func.zip $func/__main__.py 
        mv $func.zip $func/
        echo "Successfully built $func\n"

    done 
fi 

cd $workdir 
# Run the functions 
run=true 

if $run; then 

    for func in "${func_names[@]}"
    do 
        cd $workdir/$func 
        echo "Creating action $func ...."
        wsk -i action create --docker nivekiba/python3action:magick $func $func.zip 
        echo "Successfully created $func. Proceeding with the execution with the respective inputs"

        img_array = ['1KB.jpg', '16KB.jpg', '32KB.jpg', '64KB.jpg', '126KB.jpg', '257KB.jpg', '517KB.jpg', '1.3MB.jpg', '2MB.jpg', '3.2MB.jpg']

        for imgNames in "${imgNames[@]}"
        do 
            echo "Running action with image $imgNames"
            wsk -i action invoke --blocking $func --param url $1 img $imgNames  2>&1 | tee results.$func._$imgNames 
        done 

        echo "Finished running $func with all available inputs. Check the results in the following files"
        ls -la | grep -i results 
        echo "Waiting $inter_func_wait, before proceeding with the next function"
        sleep $inter_func_wait
    done 
fi 
