/**
 * Jupyter require core module
 *
 * @module
 * @summary     Require
 * @description Jupyter library and magic extension for managing linked JavaScript and CSS scripts and styles.
 * @version     0.1.0
 * @file        require/core.js
 * @author      Marek Cermak
 * @contact     macermak@redhat.com
 * @copyright   Copyright 2019 Marek Cermak <macermak@redhat.com>
 *
 * This source file is free software, available under the following license:
 *   MIT license
 *
 * This source file is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 * or FITNESS FOR A PARTICULAR PURPOSE. See the license files for details.
 *
 * For details please refer to: https://github.com/CermakM/jupyter-require
 */


define(['base/js/namespace', 'jquery', 'require', './events'], function(Jupyter, $, requirejs, em) {
    'use strict';

    const comm_manager = Jupyter.notebook.kernel.comm_manager;


    /**
     * Load required libraries
     *
     * This function pauses execution of Jupyter kernel
     * until require libraries are loaded
     *
     * @param config {Object} - requirejs configuration object
     */
    let load_required_libraries = function (config) {
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

                tid = setTimeout(errback, 5000);
                iid = setInterval(() => require([lib], callback), 250);

            });

            defined.push(p);

        });

        return Promise.all(defined).then(
            (values) => {
                console.log('Success: ', values);
                em.trigger.config(config);
            }).catch(console.error);
    };

    /**
     * Register comm for messages from Python kernel
     *
     * @param target {string} - target as specified in `Comm`
     * @param func {function} - function to be called on received message
     * @param callback {function} - callback function
     */
    let register_target = function(target, func, callback) {
        comm_manager.register_target(target,
            (comm, msg) => {
                console.debug(comm, msg);

                comm.on_msg((msg) => {
                    // figure out which cell triggered this
                    let cell = null;
                    let selected_cell = Jupyter.notebook.get_selected_cell();
                    let messages = selected_cell.metadata.messages;

                    if (messages && messages.some((d) => d.content.comm_id === comm.comm_id)) {
                        cell = selected_cell;
                    } else {
                        cell = Jupyter.notebook.get_prev_cell(selected_cell);
                    }

                    callback = callback || console.debug;

                    func(msg.content.data)
                        .then(() => callback(cell, msg))
                        .catch(console.error);

                });
            }
        );

        console.debug(`Comm '${target}' registered.`);
    };


    return {
        load_required_libraries: load_required_libraries,
        register_target: register_target
    };

});
