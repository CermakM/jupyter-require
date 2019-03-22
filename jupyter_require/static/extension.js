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
    let Jupyter = require('base/js/namespace');


    /**
     * Initialize requirements in existing cells
     *
     */
    async function init_existing_cells() {
        let cells = Jupyter.notebook.get_cells();

        cells.forEach((cell) => {
            let required = core.get_cell_requirements(cell);

            if (required.length > 0) {
                console.debug("Checking libraries required by cell: ", cell, required);
                required.forEach(async lib => {
                    let is_defined = require.defined(lib);
                    console.debug(`Checking library: ${lib}`, is_defined ? '✓' : 'x');

                    if (is_defined) {
                        // now update the output with already loaded libraries
                        // core.restore_output(cell);
                    }
                });
            }

            cell.running = false;
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
                './event_manager',
                './core',
            ], function (Jupyter, events, em, core) {

                const config = core.get_notebook_config();

                core.register_targets();
                core.register_events();

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
