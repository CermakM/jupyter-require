/**
 * Jupyter require display module
 *
 * @module
 * @summary     Require
 * @description Jupyter library and magic extension for managing linked JavaScript and CSS scripts and styles.
 * @version     0.1.0
 * @file        require/display.js
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


define(['underscore'], function(_) {

    // mime types
    const MIME_JAVASCRIPT = 'application/javascript';
    const MIME_HTML = 'text/html';
    const MIME_TEXT = 'text/plain';

    const mime_types = {
        MIME_JAVASCRIPT: MIME_JAVASCRIPT,
        MIME_HTML: MIME_HTML,
        MIME_TEXT: MIME_TEXT,
    };

    /**
     * Object storing output display data and metadata
     *
     * @param js {Function} - script to be executed in cell context
     * @param html {Element} - DOM element to be appended
     * @returns {Object}
     */
    function DisplayData(js, html) {
        this.data = {
            [MIME_TEXT]: "<JupyterRequire.display.DisplayData object>",
        };
        this.metadata = {
            display: {
                [MIME_JAVASCRIPT]: js,
                [MIME_HTML]: html,
            }
        };

        this.output_type = 'display_data';
        this.transient = undefined;
    }

    /**
     * Object storing frozen state of DisplayData
     *
     * This object can be serialized into JSON and persists
     * after notebook is saved.
     *
     * @returns {Object}
     */
    function FrozenOutput(display_data) {
        this.data = {
            [MIME_TEXT]: "<JupyterRequire.display.FrozenOutput object>",
        };

        if (_.has(display_data, MIME_HTML)) {
            this.data[MIME_HTML] = $(display_data[MIME_HTML])
                .addClass('frozen_output')
                .html();
        }
        this.metadata = {};

        this.output_type = 'display_data';
        this.transient = undefined;
    }

    let create_output_subarea = function(cell, toinsert) {
        let output_area = cell.output_area;
        let output = output_area.create_output_area();

        if (toinsert === undefined) {
            toinsert = output_area.create_output_subarea(
                {}, "output_javascript rendered_html", MIME_JAVASCRIPT);
        }

        output_area.keyboard_manager.register_events(toinsert);
        output_area.element.append(output);

        output.append(toinsert);

        return toinsert;
    };

    let freeze_display_data = function(cell) {
        return new Promise((resolve) => {
            if (cell.cell_type !== 'code') resolve();

            let outputs = cell.output_area.outputs;
            outputs.forEach((output) => {
                let display_data = output.metadata.display;
                if (display_data !== undefined)
                    output.metadata.frozen_output = new FrozenOutput(display_data);
            });

            resolve();
        });
    };

    let store_cell_outputs = function(cell) {
        return new Promise((resolve, reject) => {
            if (cell.cell_type !== 'code') resolve();

            return freeze_display_data(cell)
                .then(() => {
                    let outputs = cell.output_area.outputs;

                    outputs.forEach((output, idx) => {
                        let frozen_output = output.metadata.frozen_output;

                        if (frozen_output !== undefined)
                            outputs[idx] = frozen_output;
                    });

                    resolve();
                })
                .catch(reject);
        });
    };

    let append_javascript = function(js, cell) {
        return Promise.resolve(js(cell));
    };

    let append_html = function(html, cell) {
        return Promise.resolve(create_output_subarea(cell, html));
    };

    let append_display_data = function(js, html, cell){
        cell.output_area.outputs.push(new DisplayData(js, html));
    };

    let append_map = {
        [MIME_JAVASCRIPT] : append_javascript,
        [MIME_HTML]: append_html,
    };

    let restore_cell_outputs = function(cell) {
        return new Promise((resolve) => {
            if (cell.cell_type !== 'code') resolve();

            let outputs = cell.output_area.outputs;

            cell.output_area.clear_output();

            outputs.forEach((output) => {
                let display_data = output.metadata.display;
                if (display_data !== undefined) {
                    let format_error = (err, mt) => {
                        return `Caught error for mime type '${mt}': ${err}`;
                    };

                    for (let [mime_type, t] of _.pairs(display_data)) {
                        let append = append_map[mime_type];
                        try {
                         append(t, cell); break;
                        } catch(err) { console.debug(format_error(err, mime_type)); }
                    }
                } else cell.output_area.append_output(output);
            });

            resolve();
        });
    };

    return {
        DisplayData           : DisplayData,

        mime_types            : mime_types,

        create_output_subarea : create_output_subarea,

        append_display_data   : append_display_data,
        append_html           : append_html,
        append_javascript     : append_javascript,

        freeze_display_data   : freeze_display_data,

        store_cell_outputs    : store_cell_outputs,
        restore_cell_outputs  : restore_cell_outputs,
    }
});
