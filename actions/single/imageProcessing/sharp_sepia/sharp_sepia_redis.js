const sharp = require('sharp');
const fs = require('fs');
const redis = require('redis');
const { performance } = require("perf_hooks");



function main(args) {

    let [extract_time_start, extract_time_stop ]  = [0, 0];
    let [transform_time_start, transform_time_stop ] = [0, 0];
    let [load_time_start, load_time_stop] = [0, 0];
    redisClient = redis.createClient(6379,args.url)

    let [start_time, stop_time] = [0,0];

    start_time = performance.now();

    return new Promise(function(resolve, reject) {
        extract_time_start = performance.now();

        redisClient.get(args.imgName, (err, reply) => {
            extract_time_stop = performance.now(); 

            if (reply == null) {

                console.error('Getting the image failed with status code, no existing key '+err);
                reject({msg: 'getting the image failed, no existing key'+err});
            }

            let data = []
            transform_time_start = performance.now();


            let img = sharp(new Buffer(reply,'base64'));

                img = img.recomb([
                   [0.3588, 0.7044, 0.1368],
                   [0.2990, 0.5870, 0.1140],
                   [0.2392, 0.4696, 0.0912],
                  ]);

                let fileName = process.env.__OW_ACTIVATION_ID + '.jpg';

                img.toFile(fileName)
                    .then(info => { 
                                        transform_time_stop = load_time_start = performance.now();
   
                                        let fileBinary = fs.readFileSync(fileName);
                                        
                                        redisClient.set(fileName, new Buffer(fileBinary).toString('base64'), function(err,reply){
                                        load_time_stop = stop_time = performance.now();
                                                
                                                //  console.log({
                                                //         outputsize: info.size,
                                                //         'elapsed_time' : stop_time - start_time, 
                                                //         'extract_time' : extract_time_stop - extract_time_start,
                                                //         'transform_time' : transform_time_stop - transform_time_start,
                                                //         'load_time' : load_time_stop - load_time_start
                                                // }) 
                                                 resolve({
                                                        outputsize: info.size,
                                                        'elapsed_time' : stop_time - start_time, 
                                                        'extract_time' : extract_time_stop - extract_time_start,
                                                        'transform_time' : transform_time_stop - transform_time_start,
                                                        'load_time' : load_time_stop - load_time_start
                                                    }); 
                                            

                                        })
                                 })
                    .catch(err => {
                        console.error('Writing filtered image failed:\n' + err);
                        reject({msg: 'writing filtered image failed', err: err});
                    });
            });
        })
}

exports.main = main;