const { performance } = require('perf_hooks');
const SwiftClient = require('openstack-swift-client');
const sharp = require('sharp');

// I need to return a Promise from the non-async function main, but I need to
// handle async functions with the await keyword. This is only possible from an
// async function, thus this "handler".
async function handler(resolve, reject, args, swiftclient, inputcont, outputcont) {
    let t0 = performance.now();

    let img = sharp();
    await inputcont.get(args.object, img);

    let te = performance.now();

    let tt = te;

    img = img.toFormat(args.format);
    // Force processing the image here, by reading the data via the Stream API
    // of Sharp objects. A call to toBuffer() will produce a bugged Promise that
    // makes your script hang.
    let data = []
    img.on('readable', () => {
        let chunk;
        while (null !== (chunk = img.read())) {
            data.push(chunk);
        }
    });
    let outputsize = 0;
    img.on('end', () => {
        let buff = new Buffer.concat(data);
        tt = performance.now();
        outputsize = buff.length;
    });

    await outputcont.create(args.object + '.' + args.format, img);

    let tl = performance.now();

    resolve({
        outputsize: outputsize,
        start_ms: t0,
        times: {
            extract: te - t0,
            transform: tt - te,
            load: tl - tt
        }
    });
}

function main(args) {
    let swiftclient = new SwiftClient(new SwiftClient.SwiftAuthenticator(
        args.authurl, args.user, args.key));
    let inputcont = swiftclient.container(args.incont);
    let outputcont = swiftclient.container(args.outcont);

    return new Promise(function(resolve, reject) {
        handler(resolve, reject, args, swiftclient, inputcont, outputcont);
    });
}

exports.main = main;
