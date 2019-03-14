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

    function require_configured(cell, config) {
        events.trigger(
            'require_configured.JupyterRequire', {cell: cell, config: config})
    }

    function require_loaded(config) {
        events.trigger(
            'require_loaded.JupyterRequire', {config: config})
    }

    function config_required(cell, config) {
        events.trigger(
            'config_required.JupyterRequire', {cell: cell, config: config})
    }

    return {
        trigger: {
            require_configured: require_configured,
            require_loaded: require_loaded,

            config_required: config_required,
        }
    }
});