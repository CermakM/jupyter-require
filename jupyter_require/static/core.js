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


define(['base/js/namespace', 'notebook/js/notebook', './events'], function(Jupyter, notebook, em) {
    'use strict';

    let Notebook = notebook.Notebook;

    /**
     * Get running cells
     */
    Notebook.prototype.get_running_cells = function() {
        let cells = this.get_cells();

        return cells.filter((c) => c.running);
    };

    /**
     * Get running cell indices
     */
    Notebook.prototype.get_running_cells_indices = function() {
        let cells = this.get_cells();

        return cells.filter((c) => c.running).map((c, i) => i);
    };

    /**
     * Asynchronous Function constructor
     */
    let AsyncFunction = Object.getPrototypeOf(async function(){}).constructor;


    // mime types
    const MIME_HTML = 'text/html';
    const MIME_JAVASCRIPT = 'application/javascript';

    /**
     * Register comms for messages from Python kernel
     *
     */
    function register_targets() {
        let comm_manager = Jupyter.notebook.kernel.comm_manager;

        let target = 'execute';
        comm_manager.register_target(target,
            (comm, msg) => {
                console.debug('Comm: ', comm, 'initial message: ', msg);

                comm.on_msg(async (msg) => {
                    console.debug('Comm: ', comm, 'message: ', msg);

                    // get running cell or fall back to current cell
                    let cell = null;
                    try {
                        cell = Jupyter.notebook.get_running_cells()[0];
                    } catch {
                        // fallback, may select wrong cell but better than die out
                        let selected_cell = Jupyter.notebook.get_selected_cell();

                        if (selected_cell.cell_type === 'code') {
                            cell = selected_cell;
                        } else {
                            cell = Jupyter.notebook.get_prev_cell(selected_cell);
                        }
                    }

                    let output_area = cell.output_area;

                    let output = output_area.create_output_area();
                    let toinsert = output_area.create_output_subarea(
                        {}, "output_javascript rendered_html", MIME_JAVASCRIPT);

                    output_area.keyboard_manager.register_events(toinsert);
                    output_area.element.append(output);

                    output.append(toinsert);

                    let context = {
                        cell: cell,
                        element: toinsert,
                        output_area: output_area
                    };

                    return await execute_with_requirements(msg.content.data, context)
                        .then((values) => console.debug(values))
                        .catch(console.error);
                });

                console.debug(`Comm '${target}' registered.`);
            }
        );

        target = 'config';
        comm_manager.register_target(target,
            (comm, msg) => {
                console.debug('Comm: ', comm, 'initial message: ', msg);

                comm.on_msg(async (msg) => {
                    console.debug('Comm: ', comm, 'message: ', msg);
                    return await load_required_libraries(msg.content.data)
                        .then((values) => console.debug(values))
                        .catch(console.error);
                });

                console.debug(`Comm '${target}' registered.`);
            }
        );

    }


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
     * @param config {Object}  - requirejs configuration object
     */
    async function load_required_libraries (config) {
        console.debug('Require config: ', config);

        let libs = config.paths;

        if ($.isEmptyObject(libs)) {
            return Promise.resolve("No libraries to load.");
        }

        console.log("Loading required libraries:", libs);

        require.config(config);

        console.log("Linking required libraries:", libs);

        let defined = check_requirements(Object.keys(libs));

        return await Promise.all(defined).then(
            (values) => {
                console.log('Success: ', values);
                em.trigger.config(config);
            }).catch(console.error);
    }


    /**
     * Execute JS script with requirements
     *
     * This function pauses execution of Jupyter kernel
     * until require libraries are loaded
     *
     * @param d {Object}  - data object passed to a comm msg
     * @param context {Object} - context passed from caller
     */
    async function execute_with_requirements(d, context) {
        const script = d.script;
        const required = d.required || [];

        let params = d.params || required;

        // get rid of invalid characters
        params = params.map((p) => p.replace(/[|&$%@"<>()+-.,;]/g, ""));
        // expose element to the user script
        params.push('element');

        let wrapped = new AsyncFunction(...params, script.toString());

        return await Promise.all(check_requirements(required))
            .then(async () => {
                return await new Promise(async (resolve, reject) => {
                    requirejs(required, (...args) => {
                        console.debug(
                            "Executing user script with context: ", context, 'data: ', d);
                        wrapped.apply(context.output_area, [...args, context.element])
                            .then((r) => {
                                console.debug("Success.");
                                resolve(r);
                            }).catch(reject);
                    });
                    setTimeout(reject, 5000);
                });
            })
            .catch(handle_error);
    }


    return {
        AsyncFunction             : AsyncFunction,
        register_targets          : register_targets,
        check_requirements        : check_requirements,
        load_required_libraries   : load_required_libraries,
        execute_with_requirements : execute_with_requirements,
    };

});
