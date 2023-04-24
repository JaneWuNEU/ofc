Files
---------------
    data_image_memory.csv                Contain useful information of image data for the ML part for memory prediction
    data_audio_memory.csv                Contain useful information of audio data for the ML part for memory prediction
    data_image_caching1_{1, 2}.csv       Contain useful information of image data for the ML part for caching benefits prediction
    data_image_caching2_1.csv            Contain useful information of image data for the ML part for caching benefits prediction
    data_audio_caching.csv               Contain useful information of audio data for the ML part for caching benefits prediction
    features_image.csv                   Contains the features calculated for each file
    features_audio.csv                   Contains the features calculated for each file
    images_url.csv                       Contains all url for the dataset image



Remark: We have data_image_caching1 for five image functions and data_image_caching2 for five others image functions. As the dataset takes up space we have further separated into several csv files.

We want to predict the memory to allocate for cold containers so we have to remove the hot containers for that we only take the containers which have non-null runs.init_ms.

The compressed databases can be downloaded here:
- [audio](http://171.33.88.119:90/data/sql/audio.tar.gz)
- [image](http://171.33.88.119:90/data/sql/image.tar.gz)


To create data_image_memory.csv
```bash
mysql audio -e "SELECT functions.id as function, runs.id as id,
inputs.url as url, inputs.size_B as image_size, maxmems.memory as
truth_memory, parameters.name as name, parameters.value as arguments,
runs.outputsize, runs.init_ms, runs.end_ms FROM runs INNER JOIN
(parameters, inputs, functions, (SELECT resources.run,
MAX(resources.memory_B) as memory FROM resources GROUP BY run) AS
maxmems) ON (runs.input = inputs.id AND runs.id = parameters.run AND
runs.id = maxmems.run AND runs.function = functions.id) WHERE
runs.failed = false AND runs.init_ms IS NOT NULL  " | tr '\t' ',' > data_image_memory.csv
```

To create data_audio_memory.csv
```bash
mysql audio -e "SELECT functions.id as function, runs.id as id,
inputs.url as url, inputs.size_B as image_size, maxmems.memory as
truth_memory, parameters.name as name, parameters.value as arguments,
runs.outputsize, runs.init_ms, runs.end_ms FROM runs INNER JOIN
(parameters, inputs, functions, (SELECT resources.run,
MAX(resources.memory_B) as memory FROM resources GROUP BY run) AS maxmems)
ON (runs.input = inputs.id AND runs.id = parameters.run AND
runs.id = maxmems.run AND runs.function = functions.id)
WHERE runs.failed = false AND runs.init_ms IS NOT NULL  " | tr '\t' ',' > data_audio_memory.csv
```
To create data_image_caching.csv
```bash
mysql image_caching -e "SELECT functions.id as function, runs.id as id, runs.multiruns_ID,
inputs.url as url, inputs.size_B as image_size, maxmems.memory as
truth_memory, parameters.name as name, parameters.value as arguments,
runs.outputsize, runs.init_ms, runs.end_ms, runs.loading_input_time, runs.processing_time,
runs.loading_result_time FROM runs INNER JOIN
(parameters, inputs, functions, (SELECT resources.run,
MAX(resources.memory_B) as memory FROM resources GROUP BY run) AS
maxmems) ON (runs.input = inputs.id AND runs.id = parameters.run AND
runs.id = maxmems.run AND runs.function = functions.id) WHERE
runs.failed = false  " | tr '\t' ',' > data_image_caching.csv
```
