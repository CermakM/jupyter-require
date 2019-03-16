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


from .__about__ import __version__

from .core import link_css
from .core import link_js
from .core import load_js
from .core import load_css
from .core import require


def load_ipython_extension(ipython):
    """Load the IPython extension."""
    from .magic import RequireJSMagic

    # magic: %require
    ipython.register_magics(RequireJSMagic)


def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',  # FIXME when migrated to node.js
        'dest': 'jupyter-require',
        'require': 'jupyter-require/extension'
    }]
