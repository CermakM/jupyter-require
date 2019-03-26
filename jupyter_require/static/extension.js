/**
 * Jupyter require nbextension
 *
 * @module
 * @summary     Require
 * @description Jupyter library and magic extension for managing linked JavaScript and CSS scripts and styles.
 * @version     0.1.0
 * @file        require/extension.js
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


define(function(require) {
    'use strict';

    let _       = require('underscore');
    let events  = require('base/js/events');
    let Jupyter = require('base/js/namespace');

    let core    = require('./core');
    let display = require('./display');


    function freeze_cells() {
        let cells = Jupyter.notebook.get_cells();

        return Promise.all(cells.map((cell) => display.freeze_cell_outputs(cell)))
            .then(() => console.debug("Successfully frozen cell outputs."))
            .catch(console.error);
    }

    /**
     * Finalize all cell outputs
     *
     * This function should not make any kernel related calls
     * to prevent race conditions with kernel event handlers
     * if called when kernel is interrupted or dead.
     *
     * @returns {Promise<void | never>}
     */
    function finalize_cells() {
        let cells = Jupyter.notebook.get_cells();

        return Promise.all(cells.map((cell) => display.finalize_cell_outputs(cell)))
            .then(() => {
                Jupyter.notebook.metadata.finalized = {
                    trusted   : Jupyter.notebook.trusted,
                    timestamp : _.now(),
                };
            })
            .then(() => Jupyter.notebook.save_notebook())
            .then(() => console.debug("Successfully finalized cell outputs."))
            .catch(console.error);
    }

    /**
     * Register event handlers
     *
     */
    function register_events() {
        events.on('config.JupyterRequire', (e, d) => core.set_notebook_config(d.config));
        events.on('require.JupyterRequire', (e, d) => core.set_cell_requirements(d.cell, d.require));

        events.on({
            'extension_loaded.JupyterRequire': (e, d) => {
                console.debug("Extension loaded.");
                core.communicate(e, d).catch(console.warn);
            },

            'comms_registered.JupyterRequire': (e, d) => {
                console.debug("Comm targets registered.");
                core.communicate(e, d).catch(console.warn);
            }
        });

        events.on('execute.CodeCell', (e, d) => d.cell.running = true);
        events.on('finished_execute.CodeCell', (e, d) => d.cell.running = false);

        events.on('output_added.OutputArea', (e, d) => {
            let display_data = d.output;
            if (display_data.output_type !== 'display_data') return;

            if (display_data instanceof display.DisplayData || display_data.metadata.frozen === false) {
                display_data.freeze_output();
            } else {
                if (_.isFunction(display_data.metadata.execute))
                    display.append_javascript(display_data.metadata.execute, d.output_area).then(
                        (r) => console.debug('Output appended: ', r)
                    );
            }
        });

        events.on('before_save.Notebook', freeze_cells);

        /* Finalization events

           This is a bit hackish, but it covers probable scenarios
           in which finalization is needed, like app close/reload and
           session closed and halt.
        */
        events.on({
            'kernel_dead.Session': async function () {
                console.debug("Session is dead. Finalizing outputs...");
                await finalize_cells();
            },

            'kernel_killed.Session': async function () {
                console.debug("Session closed. Finalizing outputs...");
                await finalize_cells();
            },

            'kernel_dead.Kernel': async function () {
                console.debug("Kernel is dead. Finalizing outputs...");
                await finalize_cells();
            },
        });
    }

    /**
     * Initialize requirements in existing cells
     *
     */
    function init_existing_cells() {
        let cells = Jupyter.notebook.get_cells();
        let code_cells = cells.filter(
            (c) => c.cell_type === 'code' && c.output_type === 'display_data'
        );

        code_cells.forEach(async (cell) => {
            // mark frozen outputs
            let outputs = cell.output_area.outputs;

            outputs.forEach((output) => {
                if (output.metadata.frozen === true) {
                    let element = $(output.element).find('.output_subarea');

                    // convenience for user
                    element.addClass('output_frozen');
                }
            });

            // check requirements
            let required = core.get_cell_requirements(cell);

            if (required.length > 0) {
                Promise.all(core.check_requirements(required))
                    .then((libs) => {
                        console.debug("Success:", libs);
                    }).catch((r) => new Error(r));
            }

        });
    }


    /**
     * Load extension
     *
     */
    function load_ipython_extension() {
        return new Promise((resolve) => {
            require([
                'underscore',
                'base/js/namespace',
                'base/js/events',
                './core',
            ], function (_, Jupyter, events, core) {

                const config = core.get_notebook_config();

                core.register_targets().catch(console.error);

                register_events();

                if (config !== undefined) {
                    core.load_required_libraries(config)
                        .then(() => init_existing_cells())
                        .catch(console.error);
                }

                events.trigger(
                    'extension_loaded.JupyterRequire', {timestamp: _.now()});

                resolve();
            });
        });
    }


    return { load_ipython_extension: load_ipython_extension };

});
