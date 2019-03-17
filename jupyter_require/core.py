# jupyter-require
# Copyright 2019 Marek Cermak <macermak@redhat.com>
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module for managing linked JavaScript scripts and CSS styles."""

import json
import string

from collections import OrderedDict
from pathlib import Path

from textwrap import dedent
from typing import List, Union

from IPython import get_ipython
from IPython.core.display import display, Javascript

from ipykernel.comm import Comm


Jupyter = get_ipython()
"""Current InteractiveShell instance."""


_HERE = Path(__file__).parent


class RequireJS(object):

    __LIBS = OrderedDict()
    """Required libraries."""
    __SHIM = OrderedDict()
    """Shim for required libraries."""

    def __init__(self, required: dict = None, shim: dict = None):
        """Initialize RequireJS."""
        # comm messages
        self._msg = None
        self._msg_received = None

        # check if running in Jupyter notebook
        self._is_notebook = Jupyter and Jupyter.has_trait('kernel')

        # comms
        self._config_comm = None
        self._execution_comm = None

        if self._is_notebook:
            self._config_comm = create_comm(
                target='config', callback=self._store_callback)
            self._execution_comm = create_comm(
                target='execute', callback=self._store_callback)

        # update with default required libraries
        self.config(required or {}, shim or {})

    def __call__(self, library: str, path: str, *args, **kwargs):
        """Links JavaScript library to Jupyter Notebook.

        The library is linked using requireJS such as:

        ```javascript
        require.config({ paths: {<key>: <path>} });
        ```

        Please note that <path> does __NOT__ contain `.js` suffix.

        :param library: str, key to the library
        :param path: str, path (url) to the library without .js suffix
        """
        self.config({library: path}, shim=kwargs.pop('shim', {}))

    @property
    def libs(self) -> dict:
        """Get custom loaded libraries."""
        return dict(self.__LIBS)

    @property
    def shim(self) -> dict:
        """Get shim defined in requireJS config."""
        return dict(self.__SHIM)

    def display_context(self):
        """Print defined libraries."""
        _ = self  # ignore

        return display(Javascript("""
            const context = require.s.contexts._.defined;

            $(element).html(
                JSON.stringify(Object.keys(context).sort())
                .replace(/,/g, '<br>'));
        """))

    def config(self, libs: dict, shim: dict = None):
        """Links JavaScript libraries to Jupyter Notebook.

        The libraries are linked using requireJS such as:

        ```javascript
        require.config({
            paths: {
                <key>: <path>
            },
            shim: {
                <key>: [<dependencies>]
            }
        });
        ```

        Please note that <path> does __NOT__ contain `.js` suffix.
        """
        self.__LIBS.update(libs)
        self.__SHIM.update(shim or {})

        # data to be passed to require.config()
        self._msg = {'paths': self.__LIBS, 'shim': self.__SHIM}

        if self._is_notebook:
            self._config_comm.send(data=self._msg)

    def pop(self, lib: str):
        """Remove JavaScript library from requirements.

        :param lib: key as passed to `config()`
        """
        self.__LIBS.pop(lib)
        self.__SHIM.pop(lib)

    @classmethod
    def reload(cls, clean=False):
        """Reload and create new require object."""
        global require

        if clean:
            require = cls()
        else:
            require = cls(required=require.libs, shim=require.shim)

        require.__doc__ = RequireJS.__call__.__doc__

        return require

    def _store_callback(self, msg):
        """Store callback from comm."""
        self._msg_received = msg


class JSTemplate(string.Template):
    """Custom d3 string template."""

    delimiter = "$$"

    def __init__(self, template: str):
        super().__init__(template)

        self._safe_substitute = self.safe_substitute

        # prototype
        def safe_substitute(*args, **kws):
            """Safely substitute JS template variables."""
            kwargs = {
                key: sub if sub is not None else 'null'
                for key, sub in kws.items()
            }

            return self._safe_substitute(*args, **kwargs)

        self.safe_substitute = safe_substitute


def create_comm(target: str,
                data: dict = None,
                callback: callable = None,
                **kwargs):
    """Create ipykernel message comm."""
    # create comm on python site
    comm = Comm(target_name=target, data=data, **kwargs)
    comm.on_msg(callback)

    return comm


def execute_with_requirements(script: str, required: Union[list, dict], configured=True, **kwargs):
    """Link required libraries and execute JS script.

    :param script: JS script to be executed
    :param required: list or dict (for requireJS config) of requirements
    :param configured: bool, whether requirements are already configured

        This speeds up the execution, so if the requirements are already configured,
        do not run configuration again.

        Assume True, as user is expected to run `require.config()`
        at the initialization time.

    :param kwargs: optional keyword arguments passed to config and parser
    """
    if not configured:
        if isinstance(required, dict):
            require.config(required, **kwargs)
        else:
            raise TypeError(
                f"Attribute `required` expected to be dict, got {type(required)}.")

    required: list = required if isinstance(required, list) else list(required.keys())

    params = kwargs.pop('params', []) or required
    params = map(lambda s: s.rsplit('/')[-1], params)
    params = ', '.join(params) \
        .replace("'", '') \
        .replace('-', '_') \
        .replace('.', '_')

    script = JSTemplate(script).safe_substitute(**kwargs)

    data = {
        'script': script,
        'required': required,
        'params': params,
    }

    # noinspection PyProtectedAccess
    return require._execution_comm.send(data)  # pylint: disable=protected-access


def execute(script: str, **kwargs):
    """Execute JS script.

    This functions implicitly loads libraries defined in requireJS config.
    """
    required = []
    try:
        required = list(require.libs.keys())
    except NameError:  # require has not been defined yet, allowed
        pass

    return execute_with_requirements(script, required=required, **kwargs)


def link_css(stylesheet: str, attrs: dict = None):
    """Link CSS stylesheet."""
    script = (
        "'use strict';"
        
        f"const href = \"{stylesheet}\";"
        f"const attributes = {attrs};"
        """
        let link = document.createElement("link");
        link.rel = "stylesheet";
        link.type = "text/css";
        try {
            link.href = requirejs.toUrl(href, 'css');
        } catch (error) {
            link.href = href;
        }
        
        Object.entries(attributes)
            .forEach( ([attr, val]) => $(link).attr(attr, val) );
        
        document.head.appendChild(link);
        """
    )

    return display(Javascript(script))


def link_js(lib: str):
    """Link JavaScript library."""
    script = (
        "'use strict';"
        
        f"const src = \"{lib}\";"
        """
        let script = document.createElement("script");
        script.src = src;

        document.head.appendChild(script);
        """
    )

    return display(Javascript(script))


def load_css(style: str, attrs: dict = None):
    """Create new style element and add it to the page."""
    attrs = attrs or {}

    script = (
        "'use strict';"
        
        f"const style = `{style}`;"
        f"const attributes = {attrs};"
        """
        let id = attributes.id;
        let elem_exists = id ? $(`style#${id}`).length > 0 : false;
        
        let e = elem_exists ? document.querySelector(`style#${id}`)
                            : document.createElement(\"style\");
        
        $(e).text(`${style}`).attr('type', 'text/css');
        
        Object.entries(attributes)
            .forEach( ([attr, val]) => $(e).attr(attr, val) );

        if (!elem_exists) document.head.appendChild(e);
        """
    )

    return display(Javascript(script))


def load_js(script: str, attrs: dict = None):
    """Create new script element and add it to the page."""
    attrs = attrs or {}

    # escape dollar signs inside ticks and ticks
    script = script \
        .replace('`', '\`') \
        .replace('${', '\${')

    script_wrapped = (
        "'use strict';"

        f"const script = `{script}`;"
        f"const attributes = {attrs};"
        """
        let id = attributes.id;
        let elem_exists = id ? $(`script#${id}`).length > 0 : false;
        
        let e = elem_exists ? document.querySelector(`script#${id}`)
                            : document.createElement(\"script\");
        
        $(e).text(`${script}`).attr('type', 'text/javascript');
        
        Object.entries(attributes)
            .forEach( ([attr, val]) => $(e).attr(attr, val) );

        if (!elem_exists) document.head.appendChild(e);
        """
    )

    return display(Javascript(script_wrapped))


def wait_for(script: str, timeout: int = None, **kwargs):
    """Execute given script and wait for it to finish or timeout.

    This function pauses the IPython kernel until the script
    returns.

    :param script: str, JS script to execute
    :param timeout: int, timeout in ms, if exceeded, raises TimeOutError

    :raises TimeOutError
    """


require = RequireJS()
require.__doc__ = RequireJS.__call__.__doc__
