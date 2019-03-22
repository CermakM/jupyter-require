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

    let EventManager = function(events) {
        this.events = events;
    };

    EventManager.prototype.on = function() {
        return this.events.on.apply(arguments);
    };

    EventManager.prototype.trigger = function() {
        return this.events.on.trigger(arguments);
    };

    /**
     * Trigger event which sets requireJS configuration
     *
     * @param config
     */
    EventManager.prototype.trigger_config = function (config) {
        events.trigger(
            'config.JupyterRequire', {config: config})
    };


    /**
     * Trigger event which sets requirement for the given cell
     *
     * @param cell
     * @param required
     */
    EventManager.prototype.trigger_require = function (cell, required) {
        events.trigger(
            'require.JupyterRequire', {cell: cell, require: required})
    };

    return new EventManager(events);
});