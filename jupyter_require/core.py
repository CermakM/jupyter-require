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

_is_notebook = Jupyter and Jupyter.has_trait('kernel')

class CommError(Exception):
    """Base class for Comm related exceptions."""

    def __init__(self, *args, **kwargs):
        msg = ". ".join([
            *args[:1],
            "HINT: Try reloading <F5> the window."
        ])

        args = msg, *args[1:]
        super().__init__(*args, **kwargs)


class RequireJS(object):

    __instance = None

    __LIBS = OrderedDict()
    """Required libraries."""
    __SHIM = OrderedDict()
    """Shim for required libraries."""

    # Comms strictly require to be shared between instances
    __config_comm = None
    __execution_comm = None
    __safe_execution_comm = None

    __is_initialized = False

    def __new__(cls, required: dict = None, shim: dict = None):
        """Initialize RequireJS."""
        if cls.__instance is None:
            # initialize
            cls.__instance = super(RequireJS, cls).__new__(cls)

        if not _is_notebook:
            msg = "Jupyter Require found itself running outside of Jupyter."

            logger.critical(msg)
            raise EnvironmentError(msg)

        # update with default required libraries
        cls.__LIBS.update(required or {})
        cls.__SHIM.update(shim or {})

        return cls.__instance

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
    def is_initialized(self) -> bool:
        """Return whether RequireJS has been initialized."""
        return RequireJS.__is_initialized

    @is_initialized.setter
    def is_initialized(self, state: bool):
        """Set whether requireJS has been initialized."""
        if state and any([
            RequireJS.__config_comm is None,
            RequireJS.__execution_comm is None,
            RequireJS.__safe_execution_comm is None
        ]):
            raise ValueError(
                "Some comms have not been initialized yet."
                "Can't set to True."
            )

        if not state and not any([
            RequireJS.__config_comm is None,
            RequireJS.__execution_comm is None,
            RequireJS.__safe_execution_comm is None
        ]):
            raise ValueError("All comms are initialized. Can't set to False.")

        RequireJS.__is_initialized = state

    @property
    def libs(self) -> dict:
        """Get custom loaded libraries."""
        return dict(RequireJS.__LIBS)

    @property
    def shim(self) -> dict:
        """Get shim defined in requireJS config."""
        return dict(RequireJS.__SHIM)

    @property
    def execution_comm(self) -> Comm:
        """Return execution Comm."""
        return RequireJS.__execution_comm

    @property
    def safe_execution_comm(self) -> Comm:
        """Return execution Comm."""
        return RequireJS.__safe_execution_comm

    def display_context(self):
        """Print defined libraries."""
        _ = self  # ignore

        return display(Javascript("""
            const context = require.s.contexts._.defined;

            $(element).html(
                JSON.stringify(Object.keys(context).sort())
                .replace(/,/g, '<br>'));
        """))

    def config(self, paths: dict, shim: dict = None):
        """Links JavaScript libraries to Jupyter Notebook.

        This is Python binding for JS RequireJS `require.config` call.

        For convenience, the paths and shim are split into two separate arguments. If you
        with to use the function in a more standard JS way, consider the following example.

        Example:
        ```
        require.config(**{
            "paths": {
                <key>: <path>
            },
            "shim": {
                <key>: [<dependencies>]
            }
        });
        ```

        Please note that <path> does __NOT__ contain `.js` suffix.
        """
        logger.debug("Configuration requested: %s", {
            "paths": paths,
            "shim": shim
        })

        if not self.is_initialized:
            raise CommError("Comms haven't been initialized properly.")

        RequireJS.__LIBS.update(paths)
        RequireJS.__SHIM.update(shim or {})

        # data to be passed to require.config()
        data = {'paths': RequireJS.__LIBS, 'shim': RequireJS.__SHIM}

        if RequireJS.__config_comm is None:
            raise CommError("Comm 'config' is not open.")

        RequireJS.__config_comm.send(data=data)

    def pop(self, lib: str):
        """Remove JavaScript library from requirements.

        :param lib: key as passed to `config()`
        """
        RequireJS.__LIBS.pop(lib)
        RequireJS.__SHIM.pop(lib)

    @classmethod
    def reload(cls, clear=False):
        """Reload and create new require object."""
        logger.info("Reloading.")

        libs = cls.__LIBS if not clear else []
        shim = cls.__SHIM if not clear else []

        if clear:
            cls.__LIBS.clear()
            cls.__SHIM.clear()

        cls.__config_comm = None
        cls.__execution_comm = None
        cls.__safe_execution_comm = None

        cls.__is_initialized = False

        self = cls(required=libs, shim=shim)

        if _is_notebook:
            self._initialize_comms()

    def _initialize_comms(self):
        """Initialize Python-JavaScript comms."""
        logger.info("Initializing comms.")

        now = datetime.now()

        RequireJS.__config_comm = create_comm(
            target='config',
            comm_id=f'config.JupyterRequire#{datetime.timestamp(now)}',
            callback=RequireJS.log_callback)

        RequireJS.__execution_comm = create_comm(
            target='execute',
            comm_id=f'execute.JupyterRequire#{datetime.timestamp(now)}',
            callback=RequireJS.log_callback)

        RequireJS.__safe_execution_comm = create_comm(
            target='safe_execute',
            comm_id=f'safe_execute.JupyterRequire#{datetime.timestamp(now)}',
            callback=RequireJS.log_callback)

        self.is_initialized = True

        # initial configuration
        self.config(paths={})

        logger.info("Comms have been successfully initialized.")

    @classmethod
    def log_callback(cls, msg):
        """Store callback from comm."""
        logger.debug("Callback received: %s", msg)


require = RequireJS()
require.__doc__ = RequireJS.__call__.__doc__


class JSTemplate(string.Template):
    """Custom JS string template."""

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


def execute_with_requirements(script: str, required: Union[list, dict], silent=False, configured=True, **kwargs):
    """Link required libraries and execute JS script.

    :param script: JS script to be executed
    :param required: list or dict (for requireJS config) of requirements
    :param silent: whether the script should be executed in the silent mode

        If the script is executed as "silent", it does not run in a cell context
        and therefore it is not stored and the output is hidden from the user

    :param configured: bool, whether requirements are already configured

        This speeds up the execution, so if the requirements are already configured,
        do not run configuration again.

        Assume True, as user is expected to run `require.config()`
        at the initialization time.

    :param kwargs: optional keyword arguments for template substitution
    """
    requirejs = RequireJS()

    if not configured:
        if isinstance(required, dict):
            requirejs.config(required, **kwargs)
        else:
            raise TypeError(
                f"Attribute `required` expected to be dict, got {type(required)}.")

    required: list = required if isinstance(
        required, list) else list(required.keys())

    params = kwargs.pop('params', []) or required
    params = list(map(lambda s: s.rsplit('/')[-1], params))

    script = JSTemplate(script).safe_substitute(**kwargs)

    data = {
        'script': script,
        'silent': silent,
        'require': required,
        'parameters': params,
    }

    if requirejs.safe_execution_comm is None:
        raise CommError("Comm 'execute' is not open.")

    # noinspection PyProtectedAccess
    return requirejs.execution_comm.send(data)  # pylint: disable=protected-access


def execute(script: str, **kwargs):
    """Execute JS script.

    This function implicitly loads libraries defined in requireJS config.
    """
    requirejs = RequireJS()

    required = []

    try:
        required = list(requirejs.libs.keys())
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
    requirejs = RequireJS()

    script = "{ " + script + " }"  # provide local scope
    script = JSTemplate(script).safe_substitute(**kwargs)

    if requirejs.safe_execution_comm is None:
        raise CommError("Comm 'execute' is not open.")

    # noinspection PyProtectedAccess
    return requirejs.safe_execution_comm.send(data={'script': script})  # pylint: disable=protected-access


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

        logger.debug(
            "Requested message handler.\n\tData: %r\n\tEvent: %r", data, event)

        response = {'resolved': True, 'value': None, 'success': False}
        try:
            _, namespace = event['type'], event['namespace']

            if namespace == 'JupyterRequire':
                response['success'] = True

            logger.debug("Success.")

        except Exception as err:
            logger.error(
                "Error: '%s': %s", event, err)
            response['value'] = err

        finally:
            RequireJS.log_callback(msg)

        comm.send(response)
