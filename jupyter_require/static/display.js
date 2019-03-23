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
     * Get display data
     *
     * @returns {Object}
     */
    function DisplayData(js, html) {
        this.data = {
            [MIME_TEXT]: "<JupyterRequire.display.DisplayData object>",
        };
        this.metadata = {
            display: {
                [MIME_JAVASCRIPT]: js,
                [MIME_HTML]: html
            }
        };
        this.output_type = 'display_data';
        this.transient = undefined;
    }

    let append_javascript = function(cell, js){
        let display_data = new DisplayData(js);

        cell.output_area.outputs.push(display_data);
    };

    let append_html = function(cell, html){
        let display_data = new DisplayData(undefined, html);

        cell.output_area.outputs.push(display_data);
    };

    let append_display_data = function(cell, js, html){
        let display_data = new DisplayData(js, html);

        cell.output_area.outputs.push(display_data);
    };

    return {
        DisplayData         : DisplayData,

        append_display_data : append_display_data,
        append_html         : append_html,
        append_javascript   : append_javascript,

        mime_types          : mime_types
    }
});
