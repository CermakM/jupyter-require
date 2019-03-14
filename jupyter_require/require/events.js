/**
 * Jupyter require events module
 *
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


define(['base/js/events'], function(events) {

    function _config(config) {
        events.trigger(
            'config.JupyterRequire', {config: config})
    }

    function _require(cell, required) {
        events.trigger(
            'require.JupyterRequire', {cell: cell, require: required})
    }

    return {
        trigger: {
            config: _config,
            require: _require
        }
    }
});