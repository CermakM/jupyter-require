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


define([
    'base/js/namespace',
    'base/js/events',
    'notebook/js/notebook',
], function(Jupyter, events, notebook) {
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
     * Get notebook requireJS config
     *
     * @returns {Object} - requirejs configuration object
     */
    function get_notebook_config() { return Jupyter.notebook.metadata.require || {}; }

    /**
     * Set notebook requireJS config
     *
     * @param config {Object} - requirejs configuration object
     */
    function set_notebook_config(config) { Jupyter.notebook.metadata.require = config; }

    /**
     * Asynchronous Function constructor
     */
    let AsyncFunction = Object.getPrototypeOf(async function(){}).constructor;


    /**
     * Get cell requirement metadata
     *
     * @param cell {CodeCell} - notebook cell
     */
    function get_cell_requirements(cell) { return cell.metadata.require || []; }


    /**
     * Set cell requirement metadata
     *
     * @param cell {CodeCell} - notebook cell to update metadata
     * @param required {Object} - requirements config object
     */
    function set_cell_requirements(cell, required) { cell.metadata.require = required; }


    /**
     *  Check cell requirements
     * @param required {Array} - array of requirements
     * @returns {Array}
     */
    function check_requirements(required) {
        let cell = Jupyter.notebook.get_selected_cell();

        if (required.length > 0) events.trigger('require.JupyterRequire', {cell: cell, require: required});

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

    /**
     * Handle error and output it to the notebook cell
     * @param error
     */
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
                events.trigger('config.JupyterRequire', {config: config});
            }).catch(handle_error);
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
        const required = d.require || [];

        let params = d.parameters || required;

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

    // mime types
    const MIME_JAVASCRIPT = 'application/javascript';
    const MIME_HTML = 'text/html';
    const MIME_TEXT = 'text/plain';


    const default_output = {
        data: {
            [MIME_TEXT]: "<IPython.core.display.Javascript object>"  // be consistent here
        },
        execution_count: null,
        metadata: {},
        output_type: 'execute_result',
        transient: undefined
    };


    /**
     * Get cell output HTML from div.output
     *
     * @param cell {CodeCell} - notebook cell
     * @returns {*} DOM div.output element
     */
    function get_cell_output(cell) {
        return cell.output_area.element.get(0);
    }

    /**
     * Append output HTML to div.output of the cell output area
     *
     * @param cell {CodeCell} - notebook cell
     * @param output html to be stored in div.output
     */
    function append_output(cell, output) {
        $(cell.output_area.element.get(0)).html(output);
    }

    /**
     * Save cell outputs for future restore
     *
     * @param cell {CodeCell} - notebook cell
     */
    function save_cell_output_metadata(cell) {
        if (!(cell.cell_type === 'code' && cell.metadata.require !== undefined)) return;

        let html_output = get_cell_output(cell);

        cell.metadata.display = {
            [MIME_HTML]: html_output,
            [MIME_TEXT]: default_output,
        };
    }

    /**
     * Save cell execution metadata
     *
     * @param cell {CodeCell} - notebook cell
     * @param data {CodeCell} - execution data
     */
    function save_cell_execution_metadata(cell, data) {
        let required = cell.metadata.require;
        if (!(cell.cell_type === 'code' && required !== undefined)) return;

        cell.metadata.execute = {
            [MIME_JAVASCRIPT]: data
        }
    }

    function save_cell_metadata() {
        let cells = Jupyter.notebook.get_cells();

        return new Promise((resolve) => {
            cells.forEach((c) => {
                save_cell_output_metadata(c);
                save_cell_execution_metadata(c);
            });

            resolve();
        });
    }

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
                    let cell = Jupyter.notebook.get_running_cells()[0];
                    console.debug('cell:', cell);

                    if (!cell) {
                        // fallback, may select wrong cell but better than die out
                        let selected_cell = Jupyter.notebook.get_selected_cell();

                        if (selected_cell.cell_type === 'code') {
                            cell = selected_cell;
                        } else {
                            cell = Jupyter.notebook.get_prev_cell(selected_cell);
                        }
                    }

                    console.debug('cell:', cell);
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

                    output_area.outputs.push(default_output);

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


    return {
        AsyncFunction             : AsyncFunction,

        get_cell_requirements     : get_cell_requirements,
        set_cell_requirements     : set_cell_requirements,

        save_cell_metadata        : save_cell_metadata,

        get_notebook_config       : get_notebook_config,
        set_notebook_config       : set_notebook_config,

        check_requirements        : check_requirements,
        execute_with_requirements : execute_with_requirements,

        load_required_libraries   : load_required_libraries,

        register_targets          : register_targets,
    };

});
