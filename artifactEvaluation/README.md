# Artifact Evaluation Process 
The main entry point of FAASCache can be found [here](https://gitlab.com/lenapster/faascache/).

This documentation is a small guide for helping the members of the AEC. The main claims of our paper concerns our machine learning algorithm prediction accuracy and the improvement in terms of execution times for serverless functions. Withstanding this, we divide this guide in two parts: **Machine Learning** and **Cache internal metrics**.

## Machine Learning 
> This section mainly concerns Figure 4, 5 (and in general Section 6.1 of our paper.)

As our paper states, we rely on **J48** to predict functions memory usage. All machine learning related code sits in [machine-learning](https://gitlab.com/lenapster/faascache/-tree/master/machine-learning) folder. 

To check our model **accuracy and maturation time**, follow the corresponding [jupyter notebook](https://gitlab.com/lenapster/faascache/-/blob/master/machine-learning/evaluation.ipynb) that computes all the necessary metrics based on our datasets. 

Please give us any feedback on our model if you test with custom datasets.



## Cache benefits
> This section mainly concers Figure 6,7,8, and Table 4 (and in general Section Section 6.2 of our paper)

*To proceed with this section, it is mandatory to have a complete installation of FaaSCache on your testbed. To achieve this, please follow the instructions on our [wiki](https://gitlab.com/lenapster/faascache/).*

### FaaSCache speedup (Figure 6).

In our paper, Figure 6 plots for several functions, [single stage](https://gitlab.com/lenapster/faascache/-/tree/master/actions/single/imageProcessing) --- (wand_blur, wand_resize, wand_sepia, wand_rotate, wand_denoise, and wand-edge) --- and [multi-stage](https://gitlab.com/lenapster/faascache/-/tree/master/actions/workflows); their **execution times** against their **input sizes**, using *[OpenStackSwift](https://gitlab.com/lenapster/faascache/-/tree/master/IMOC/OpenStackSwift)* as the remote storage. We run the results under four configurations

* Standart OpenWhisk setup (1)
* Standart OpenWhisk + Redis as the remote storage (2)
* FaaSCache under three conditions (S1,S2, and S3 --- please refer to the paper for further explanations.)

#### (1) Getting Standart Openwhisk execution times.

* Build and install a standart openwhisk in cluster mode (powered by kubernetes). 
* Ensure you have OpenStackSwift (your can use our modified version) up and note the endpoint @END_POINT_SWIFT 
* On the openwhisk controller node, open a console then
```
cd $FAASCACHE_DIR/actions/single/imageProcessing/Swift
```
* Load inputs into OpenStackSwift. To do that, type 
```s
chmod +x loadInputs.sh; ./loadInputs.sh @END_POINT_SWIFT
```
where @END_POINT_SWIFT is your SWIFT Endpoint. Ex: 

```s
./loadInputs.sh http://192.168.0.142
```

* Now, your can build and run the functions : 
```s
chmod +x run.sh ; ./run.sh @ENDPOINT_SWIFT
```
* At the end of the execution, in each function folder, there will be a file **results.FUNCNAME._IMGNAME** that contains for every IMAGE, the result of the function **FUNCNAME**. Each execution provides the time for **extract, transform, and load** phase. 

#### (2) Getting Standart Openwhisk + Redis execution times 

* Install Redis in [standalone mode](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-18-04) without a password and default port **6379** (If you do, you will need to update the functions to take that into account). Note your @REDIS_ENDPOINT.
* Load the inputs to Redis, to do that, open a console and
```s
cd $FAASCACHE_DIR/actions/single/imageProcessing/Redis
```
* Then 
```s
chmod +x loadInputs.py ; ./loadInputs.py @REDIS_ENDPOINT
```
Now, you can build and run the functions: 
```s
chmod +x run.sh; ./run.sh @REDIS_ENDPOINT
```
* At the end of the execution, in each function folder, a file **redis.results.FUNCNAME._IMGNAME** that has the same content as previously.

#### (3) Getting FAASCACHE results 

* If inputs are already loaded in Swift and your FAASCache setup correctly configured (please refer to the [wiki](https://gitlab.com/lenapster/faascache/)), then do:
```s
cd $FAASCACHE_DIR/actions/single/imageProcessing/FaasCache
chmod +x run.sh
./run.sh
```
* At the end of the execution, results for every function and input size is reported in the file **faascache.results.FUNCNAME._IMGNAME**. 


### FAASCache scaling impact on function's latency (Figure 7)

To measure FAASCache's impact on function's latency, we need to populate the cache nodes till not enough memory remains for the function execution. This will trigger, the downscaling of the our cache nodes for future invocations. 

To achieve, first we need to populate RAMCloud:

* Populate the cache nodes. To achieve this, open a console and 
```s 
cd $FAASCACHE_DIR/IMOC/RAMCloud.
```
* Then run, compile the file **populate.cc**, (assuming you are in a folder where you compiled RAMCloud), 
```s
g++ -v -Lobj.master -Isrc -Iobj.master populate.cc obj.master/libramcloud.so -opopulate`
```
* Now, you can run the binary providing the **server_locator** of your RAMCloud cluster. Ex: 
```s
./populate tcp:host=192.168.77.15,port=11100
```
* This will create several objects of 1MB and store it in the different RAMCloud nodes. By default it will populate up to **500MB**, update the **populate.cc** file to meet your needs (in order to reproduce S1, S2, and S3 scenarios in the paper).
* If you're interested, you can also have raw scaling time by compiling and running the file **scalingPerfBench.cc** in the RAMCloud folder.

Once the cache is populated, you can now run the function of your choice (in our paper, we choose **wand_sepia**, but you can go with any of your choice), record the execution times and compare with a scaling-free run. 


### FAASCache scaling up/down times (Table 4)

To measure our migration routine, you just need to **scalingPerfBench.cc** in the RAMCloud folder. To achieve that, 

* First compile the latter file, assuming you're in a folder where RAMCloud is built, run 
```s
g++ -v -Lobj.master -Isrc -Iobj.master scalingPerfBench.cc obj.master/libramcloud.so -scalingPerf
``` 
* What this binary does is to first populate the cache nodes, then trigger up-scaling (and downscaling if you set *SCALING_DOWN*) by increasing the cache size by **8MB**, **64MB**, **256MB**, **512MB**, and **1GB**. The output is the time needed to perform the scaling operation. Just run the binary providing the server locator as previously. Ex:
```s
./scalingPerf tcp:host=192.168.77.15,port=11100
```
* So, to measure migration times (Table 4), populate the cache nodes depending on your testbed and initial configuration, then trigger scale downs and record the time.



### FAASLoad profiler + injector 

FaaSLoad is a load injector for OWK, which allows emulating several tenants with different loads. Overall, FaaSLoad prepares the input data (in the RSDS) for the invocations of each function, then performs the function invocations at different intervals within a given observation period. The invocation interval can be configured as periodic or based on the exponential law. 

FAASLoad at the moment is experimental, so we would like feedbacks on the difficulties encountered when deploying and using FAASLoad. FAASLoad is FAASCache-independent, you can run with and withouth. To play with FAASLoad, read the [wiki related](https://gitlab.com/lenapster/faascache/-/tree/master/FaaSLoad).

> Please, when playing with FAASCache, don't forget to use our custom python runtime as stated in [wiki-Wrapping up section](https://gitlab.com/lenapster/faascache/), and update the serverLocator file to inform FAASCache where is the RAMCloud controller node. 




