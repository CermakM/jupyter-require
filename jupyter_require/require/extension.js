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

    let Jupyter = require('base/js/namespace');
    let events  = require('base/js/events');
    let core = require('./core');

    /**
     * Register JupyterRequire comm targets
     *
     */
    function register_targets() {
        // configuration
        let events = require('./events');

        core.register_target('require', core.load_required_libraries, events.trigger.require)
    }


    /**
     * Register JupyterRequire event handlers
     *
     */
    function register_events() {
        events.on('config.JupyterRequire', (e, d) => set_notebook_metadata(d.config));
        events.on('require.JupyterRequire', (e, d) => set_cell_requirements(d.cell, d.require));
    }

    /**
     * Initialize requirements in existing cells
     *
     */
    async function init_existing_cells(cells) {
        cells.forEach((cell) => {
            let required = get_cell_requirements(cell);

            if (required.length > 0) {
                console.debug("Checking libraries required by cell: ", cell, required);
                required.forEach(async lib => {
                    let is_defined = require.defined(lib);
                    console.debug(`Checking library: ${lib}`, is_defined ? '✓' : 'x');

                    if (is_defined) {
                        // now update the output with already loaded libraries
                        update_cell_output(cell);
                    }
                });
            }
        });
    }

    /**
     * Whether current cell has requirements.
     *
     * @param cell {codeCell} - notebook cell
     * @returns {boolean}
     */
    function has_requirements(cell) { return cell.metadata.require !== undefined; }


    /**
     * Get requirejs config from notebook metadata
     *
     */
    function get_notebook_config(nb) { return nb.metadata.require || Jupyter.notebook.metadata.require; }

    /**
     * Get cell requirement metadata
     *
     * @param cell {codeCell} - notebook cell
     */
    function get_cell_requirements(cell) { return cell.metadata.require || []; }


    /**
     * Set cell requirement metadata
     *
     * @param cell {codeCell} - notebook cell to update metadata
     * @param required {Object} - requirements config object
     */
    function set_cell_requirements(cell, required) { cell.metadata.require = required; }

     /**
     * Set notebook metadata
     *
     * @param config {Object} - requirejs configuration object
     */
    function set_notebook_metadata(config) { Jupyter.notebook.metadata.require = config; }

    /**
     * Update cell output
     *
     * @param cell {codeCell} - notebook cell to update
     */
    function update_cell_output(cell) {
        if (cell.cell_type !== 'code') return;

        let outputs = cell.output_area.outputs;

        cell.output_area.clear_output();
        outputs.forEach((d) => cell.output_area.append_output(d));
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
                './events',
                './core',
            ], function (Jupyter, events, core) {

                const config = get_notebook_config(Jupyter.notebook);
                let cells = Jupyter.notebook.get_cells();

                register_targets();
                register_events();

                if (config !== undefined) {
                    core.load_required_libraries(config)
                        .then(() => init_existing_cells(cells))
                        .catch(console.error);
                }

                resolve();
            });
        });
    }


    return { load_ipython_extension: load_ipython_extension };

});
