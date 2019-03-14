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

    let core = require('./core');

    const default_targets  = {
        'config': core.load_required_libraries,
    };


    function register_targets(core) {
        Object.entries(default_targets).forEach(
            ([t, f]) => core.register_target(t, f));
    }


    /**
     * Register JupyterRequire event handlers
     *
     */
    function register_events(Jupyter, events, outputarea) {
        events.on('config_required.JupyterRequire', (e, d) => set_cell_requirements(d.cell, d.config));
    }

    /**
     * Initialize requirements in existing cells
     *
     */
    function init_existing_cells(cells) {
        cells.forEach( async cell => {
            if (cell.metadata.require) {
                let config = get_cell_requirements(cell);

                if (config) {
                    core.load_required_libraries(config).then(() => {
                        update_cell_output(cell);
                    }).catch(console.error);
                }
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
     * Get cell requirement metadata
     *
     * @param cell {codeCell} - notebook cell
     */
    function get_cell_requirements(cell) { return cell.metadata.require || {}; }


    /**
     * Set cell requirement metadata
     *
     * @param cell {codeCell} - notebook cell to update metadata
     * @param config {Object} - requirements config object
     */
    function set_cell_requirements(cell, config) { cell.metadata.require = config; }


    /**
     * Update cell output
     *
     * @param cell {codeCell} - notebook cell to update
     */
    function update_cell_output(cell) {
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
                'notebook/js/outputarea',
                './core',
            ], function (Jupyter, events, outputarea, core) {
                register_targets(core);
                register_events(Jupyter, events, outputarea);

                init_existing_cells(Jupyter.notebook.get_cells());
                resolve();
            });
        });
    }


    return { load_ipython_extension: load_ipython_extension };

});
