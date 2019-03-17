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
                    // TODO: figure out which cell triggered this
                    let cell = Jupyter.notebook.get_selected_cell();

                    callback = callback ? callback : console.debug;

                    func(msg.content.data)
                        .then(() => callback(cell, msg))
                        .catch(console.error);

                });
            }
        );

        console.debug(`Comm '${target}' registered.`);
    };


    function check_requirements(required) {
        require(['nbextensions/jupyter-require/events'], (em) => {
            let cell = Jupyter.notebook.get_selected_cell();

            if (required.length > 0) em.trigger.require(cell, required);
        });

        console.debug("Checking required libraries: ", required);

        let defined = [];  // array of promises

        required.forEach( (lib) => {

            let p = new Promise((resolve, reject) => {

                let iid, tid;

                let callback = function() {
                    clearTimeout(tid);
                    clearInterval(iid);

                    resolve(`Library '${lib}' has been linked.`);
                };
                let errback = function() {
                    clearInterval(iid);

                    reject(`Library '${lib}' could not be loaded.`);
                };

                tid = setTimeout(errback, 5000);
                iid = setInterval(() => require([lib], callback), 250);

            });

            defined.push(p);
        });

        return defined;
    }

    function handle_error(error) {
        console.error(error);

        let traceback = error.stack ? error.stack.split('\n') : [""];

        const output_error = {
            ename: 'JupyterRequireError',
            evalue: error.message || error,
            traceback: traceback,
            output_type: 'error'
        };
        let cell = Jupyter.notebook.get_selected_cell();

        // append stack trace to the cell output element
        cell.output_area.append_output(output_error);
    }

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

        let libs = config.paths;

        if ($.isEmptyObject(libs)) {
            return Promise.resolve("No libraries to load.");
        }

        console.log("Loading required libraries:", libs);

        require.config(config);

        console.log("Linking required libraries:", libs);

        let defined = check_requirements(Object.keys(libs));

        return Promise.all(defined).then(
            (values) => {
                console.log('Success: ', values);
                em.trigger.config(config);
            }).catch(console.error);
    };


    function execute_with_requirements(d) {
        // execution template
        const script = d.script;
        const required = d.required || [];
        const params = d.params || required;

        let js = `
        require(${JSON.stringify(required)}, (${params.toString()}) => {
            ${script.toString()}
        });`;

        console.log(js);

        return Promise.all(check_requirements(required))
            .then(() => {
                try {
                    eval(js);  // evaluate user script
                } catch(err) { handle_error(err); }
            })
            .catch(handle_error);
    }


    return {
        register_target           : register_target,
        check_requirements        : check_requirements,
        load_required_libraries   : load_required_libraries,
        execute_with_requirements : execute_with_requirements,
    };

});
