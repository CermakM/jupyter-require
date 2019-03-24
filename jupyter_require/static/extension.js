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

    let core    = require('./core');
    let events  = require('base/js/events');
    let Jupyter = require('base/js/namespace');


    /**
     * Register JupyterRequire event handlers
     *
     */
    function register_events() {
        events.on('config.JupyterRequire', (e, d) => core.set_notebook_config(d.config));
        events.on('require.JupyterRequire', (e, d) => core.set_cell_requirements(d.cell, d.require));

        events.on('execute.CodeCell', (e, d) => d.cell.running = true);
        events.on('finished_execute.CodeCell', (e, d) => d.cell.running = false);

        // events.on('before_save.Notebook', () => {});
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
                'base/js/namespace',
                'base/js/events',
                './core',
            ], function (Jupyter, events, core) {

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
