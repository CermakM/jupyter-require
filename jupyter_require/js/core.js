'use strict';

function load_required_libraries(config) {
    console.debug('Require config: ', config);

    let success = true;
    let libs = config.paths;

    if ($.isEmptyObject(libs)) {
        return Promise.resolve("No libraries to load.");
    }

    console.log("Loading required libraries:", libs);

    require.config(config);

    console.log("Linking required libraries:", libs);

    let defined = [];  // array of promises
    Object.keys(libs).forEach( (lib) => {

        let p = new Promise((resolve, reject) => {

            let iid, tid;

            let callback = function() {
                clearTimeout(tid);
                clearInterval(iid);

                resolve(`Library '${lib}' has been linked.`);
            };
            let errback = function() {
                clearInterval(iid);

                success = false;
                reject(`Library '${lib}' could not be loaded.`);
            };

            tid = setTimeout(errback, 2000);
            iid = setInterval(() => require([lib], callback), 100);

        });

        defined.push(p);

    });

    return Promise.all(defined).then(console.log).catch(console.error);
}
