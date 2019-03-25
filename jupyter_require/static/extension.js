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


    function freeze_cells_outputs() {
        let cells = Jupyter.notebook.get_cells();

        return Promise.all(cells.map((cell) => display.freeze_cell_outputs(cell)))
            .then(() => console.debug("Successfully frozen cell outputs."))
            .catch(console.error);
    }

    function finalize_cells_outputs() {
        let cells = Jupyter.notebook.get_cells();

        return Promise.all(cells.map((cell) => display.finalize_cell_outputs(cell)))
            .then(() => console.debug("Successfully frozen cell outputs."))
            .catch(console.error);
    }

    /**
     * Register JupyterRequire event handlers
     *
     */
    function register_events() {
        events.on('config.JupyterRequire', (e, d) => core.set_notebook_config(d.config));
        events.on('require.JupyterRequire', (e, d) => core.set_cell_requirements(d.cell, d.require));

        events.on('execute.CodeCell', (e, d) => d.cell.running = true);
        events.on('finished_execute.CodeCell', (e, d) => d.cell.running = false);

        events.on('output_added.OutputArea', (e, d) => {
            let display_data = d.output;
            if (display_data instanceof display.DisplayData || display_data.metadata.frozen === false) {
                display_data.freeze_output();
            } else {
                if (_.isFunction(display_data.metadata.execute))
                    display.append_javascript(display_data.metadata.execute, d.output_area).then(
                        (r) => console.debug('Output appended: ', r)
                    );
            }
        });

        events.on('before_save.Notebook', freeze_cells_outputs);

        events.on('finalize.JupyterRequire', async function (e, d) {
            // finalize all cells before shutdown
            let timestamp = d.timestamp;

            Jupyter.notebook.metadata.finalized = {
                trusted: Jupyter.notebook.trusted,
                timestamp: timestamp,
            };

            // this function should not make any kernel related calls
            // to prevent race conditions with Jupyter event handlers
            await finalize_cells_outputs();

            // Chrome requires returnValue to be set
            e.returnValue = true;
        });

    }


    /**
     * Initialize requirements in existing cells
     *
     */
    function init_existing_cells() {
        let cells = Jupyter.notebook.get_cells();

        cells.forEach(async (cell) => {
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

                core.register_targets();
                register_events();

                if (config !== undefined) {
                    core.load_required_libraries(config)
                        .then(() => init_existing_cells())
                        .catch(console.error);
                }

                resolve();
            });
        });
    }


    return { load_ipython_extension: load_ipython_extension };

});
