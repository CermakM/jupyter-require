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

"""Jupyter library and magic extension for managing linked JavaScript and CSS scripts and styles."""

import logging
import time

import daiquiri
import daiquiri.formatter

from .__about__ import __version__

from .notebook import link_css
from .notebook import link_js
from .notebook import load_js
from .notebook import load_css

from .core import communicate

from .core import execute_with_requirements
from .core import execute
from .core import safe_execute

from .core import require

from IPython import get_ipython


daiquiri.setup(
    level=logging.DEBUG,
    outputs=[
        daiquiri.output.File(
            level=logging.DEBUG,
            filename='.log',
            formatter=daiquiri.formatter.ColorFormatter(
                fmt="%(asctime)s [%(process)d] %(color)s%(levelname)-8.8s %(name)s:"
                    "%(lineno)d: [JupyterRequire] %(message)s%(color_stop)s"
            )),
        daiquiri.output.Stream(
            level=logging.WARN,
            formatter=daiquiri.formatter.ColorFormatter(
                fmt="%(asctime)s [%(process)d] %(color)s%(levelname)-8.8s %(name)s:"
                    "%(lineno)d: [JupyterRequire] %(message)s%(color_stop)s"
            )
        ),
    ],
)

logger = daiquiri.getLogger()


def load_ipython_extension(ipython):
    """Load the IPython Jupyter Require extension."""
    from .magic import RequireJSMagic

    logger.debug("Loading Jupyter Require extension.")

    if not hasattr(ipython, 'kernel'):
        logger.debug("No kernel found.")
        return

    register_comm_targets(ipython.kernel)
    time.sleep(0.5)  # let the JS register the targets

    # fontawesome fas icon
    link_css(
        "https://use.fontawesome.com/releases/v5.8.1/css/all.css",
        attrs={
            'integrity': "sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf",
            'crossorigin': "anonymous"
        })

    # magic: %require
    ipython.register_magics(RequireJSMagic)


def register_comm_targets(kernel=None):
    """Register comm targets."""
    if kernel is None:
        kernel = get_ipython().kernel

    logger.debug("Initializing comms.")
    # noinspection PyProtectedMember
    require._initialize_comms()  # pylint: disable=protected-access

    logger.debug("Registering comm targets.")
    kernel.comm_manager.register_target('communicate', communicate)


def _handle_ipython():
    """Register with the comm target at import."""
    ipython = get_ipython()
    if ipython is None:
        return

    load_ipython_extension(ipython)


def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',  # FIXME when migrated to node.js
        'dest': 'jupyter-require',
        'require': 'jupyter-require/extension'
    }]


_handle_ipython()
