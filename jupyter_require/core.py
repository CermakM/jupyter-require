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

import logging
import string

import daiquiri

from datetime import datetime

from collections import OrderedDict
from pathlib import Path

from typing import List, Union

from IPython import get_ipython
from IPython.core.display import display, Javascript

from ipykernel.comm import Comm

logger = daiquiri.getLogger()


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

        # comms
        self._config_comm = None
        self._execution_comm = None
        self._safe_execution_comm = None

        # update with default required libraries
        self.__LIBS.update(required or {})
        self.__SHIM.update(shim or {})

        # check if running in Jupyter notebook
        self._is_notebook = Jupyter and Jupyter.has_trait('kernel')

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

        self._config_comm.send(data=self._msg)

    def pop(self, lib: str):
        """Remove JavaScript library from requirements.

        :param lib: key as passed to `config()`
        """
        self.__LIBS.pop(lib)
        self.__SHIM.pop(lib)

    @classmethod
    def reload(cls, clear=False):
        """Reload and create new require object."""
        global require

        if clear:
            cls.__LIBS.clear()
            cls.__SHIM.clear()

        libs = require.libs if not clear else []
        shim = require.shim if not clear else []

        require = cls(required=libs, shim=shim)

        if require._is_notebook:
            require._initialize_comms()

        require.__doc__ = RequireJS.__call__.__doc__

    def _initialize_comms(self):
        """Initialize Python-JavaScript comms."""
        now = datetime.now()

        self._config_comm = create_comm(
            target='config',
            comm_id=f'config.JupyterRequire#{datetime.timestamp(now)}',
            callback=self._store_callback)

        self._execution_comm = create_comm(
            target='execute',
            comm_id=f'execute.JupyterRequire#{datetime.timestamp(now)}',
            callback=self._store_callback)

        self._safe_execution_comm = create_comm(
            target='safe_execute',
            comm_id=f'safe_execute.JupyterRequire#{datetime.timestamp(now)}',
            callback=self._store_callback)

        # initial configuration
        self.config(libs={})

    def _store_callback(self, msg):
        """Store callback from comm."""
        self._msg_received = msg


class JSTemplate(string.Template):
    """Custom d3 string template."""

    delimiter = "$$"

    def __init__(self, template: str):
        super().__init__(template)

        self._safe_substitute = self.safe_substitute
        self._substitute = self.substitute

        # prototype
        def safe_substitute(*args, **kws):
            """Safely substitute JS template variables."""
            kwargs = {
                key: sub if sub is not None else 'null'
                for key, sub in kws.items()
            }

            return self._safe_substitute(*args, **kwargs)

        # prototype
        def substitute(*args, **kws):
            """Substitute JS template variables."""
            kwargs = {
                key: sub if sub is not None else 'null'
                for key, sub in kws.items()
            }

            return self._substitute(*args, **kwargs)

        self.safe_substitute = safe_substitute
        self.substitute = substitute


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

    :param kwargs: optional keyword arguments for template substitution
    """
    if not configured:
        if isinstance(required, dict):
            require.config(required, **kwargs)
        else:
            raise TypeError(
                f"Attribute `required` expected to be dict, got {type(required)}.")

    required: list = required if isinstance(required, list) else list(required.keys())

    params = kwargs.pop('params', []) or required
    params = list(map(lambda s: s.rsplit('/')[-1], params))

    script = JSTemplate(script).safe_substitute(**kwargs)

    data = {
        'script': script,
        'require': required,
        'parameters': params,
    }

    if require._safe_execution_comm is None:
        raise TypeError("Comm 'execute' is not open.")

    # noinspection PyProtectedAccess
    return require._execution_comm.send(data)  # pylint: disable=protected-access


def execute(script: str, **kwargs):
    """Execute JS script.

    This function implicitly loads libraries defined in requireJS config.
    """
    required = []
    try:
        required = list(require.libs.keys())
    except NameError:  # require has not been defined yet, allowed
        pass

    return execute_with_requirements(script, required=required, **kwargs)


def safe_execute(script: str, **kwargs):
    """Execute JS script and treat it as safe script.

    Safe scripts are executed on cell creation
    and are therefore not allowed to have any requirements.
    Scripts executed with this method also persist through notebook
    reloads and are automatically loaded on app initialization.

    This function is convenient for automatic loading and linking
    of custom CSS and JS files.
    """
    script = "{ " + script + " }"  # provide local scope
    script = JSTemplate(script).safe_substitute(**kwargs)

    if require._safe_execution_comm is None:
        raise TypeError("Comm 'safe_execute' is not open.")

    # noinspection PyProtectedAccess
    return require._safe_execution_comm.send(data={'script': script})  # pylint: disable=protected-access


require = RequireJS()
require.__doc__ = RequireJS.__call__.__doc__


def _handle_comms_registered(*args, **kwargs):
    """Handle comms_registered.JupyterRequire event."""
    logger.debug("Comms registered.")


def _handle_extension_loaded(*args, **kwargs):
    """Handle extension_loaded.JupyterRequire event."""
    logger.debug("Extension loaded.")

    # Jupyter discards promises on window reload,
    # so comms have to be re-initialized
    require._initialize_comms()

    msg = "Comms initialized."
    logger.debug(msg)

    return msg


_event_handle_map = {
    'comms_registered': _handle_comms_registered,
    'extension_loaded': _handle_extension_loaded
}


def communicate(comm, open_msg):
    """Handle messages from Jupyter frontend."""
    _ = open_msg  # ignored

    logger.debug("Comm 'communicate' opened.")

    @comm.on_msg
    def handle_msg(msg):
        """Handle message."""
        logger.debug(
            "Message received: %r", msg)

        data = msg['content']['data']

        event = data.get('event', None)
        event_data = data.get('event_data', {})

        logger.debug(
            "Requested message handler.\n\tData: %r\n\tEvent: %r", data, event)

        response = {'resolved': True, 'value': None, 'success': False}
        try:
            event_type, namespace = event['type'], event['namespace']

            if namespace == 'JupyterRequire':
                handle = _event_handle_map[event_type]

                response['value'] = handle(event_data)
                response['success'] = True

            logger.debug("Success.")

        except Exception as err:
            logger.error(
                "Error: '%s': %s", event, err)
            response['value'] = err

        finally:
            require._store_callback(msg)

        comm.send(response)
