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
            },
            execute: _.isFunction(js),
            frozen: false
        };

        this.output_type = 'display_data';
        this.transient = undefined;
    }

    /**
     * Freeze the output and store it in the data
     *
     * The data object can be then be serialized into JSON and persists
     * after notebook is saved.
     *
     * @returns {Object}
     */
    DisplayData.prototype.freeze_output = function() {
        const elt = this.metadata.display[MIME_HTML];
        let frozen_output = {
            [MIME_TEXT]: "<JupyterRequire.display.DisplayData object>",
        };

        if (elt !== undefined) {
            frozen_output[MIME_HTML] = $(elt).addClass('frozen_output').html();
        }

        this.data = frozen_output;
        this.metadata.frozen = true;
    };

    let create_output_subarea = function(output_area, toinsert) {
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

    let freeze_cell_outputs = function(cell) {
        return new Promise((resolve) => {
            if (cell.cell_type !== 'code') resolve();

            let outputs = cell.output_area.outputs;

            outputs.forEach((output) => {
                if (output instanceof DisplayData)
                    output.freeze_output();
            });

            resolve();
        })
    };

    let append_javascript = function(js, output_area) {
        return Promise.resolve(js(output_area));
    };

    let append_html = function(html, output_area) {
        return Promise.resolve(create_output_subarea(output_area, html));
    };

    let append_display_data = function(js, html, output_area){
        let output = new DisplayData(js, html);

        output_area.outputs.push(output);

        output_area.events.trigger('output_added.OutputArea', {
            output_area: output_area,
            output: output
        });
    };


    return {
        DisplayData           : DisplayData,

        mime_types            : mime_types,

        create_output_subarea : create_output_subarea,

        append_display_data   : append_display_data,
        append_html           : append_html,
        append_javascript     : append_javascript,

        freeze_cell_outputs   : freeze_cell_outputs,
    }
});
