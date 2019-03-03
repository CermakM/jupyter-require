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

"""Jupyter magic for managing linked JavaScript scripts and CSS styles."""

import re

from IPython.core.magic import cell_magic
from IPython.core.magic import line_magic
from IPython.core.magic import magics_class
from IPython.core.magic import Magics
from IPython.core.magic import needs_local_scope

from .core import link_css
from .core import link_js
from .core import load_js
from .core import load_css
from .core import require


@magics_class
class RequireJSMagic(Magics):
    """Ipython magic for RequireJS class.

    Links JavaScript libraries to Jupyter Notebook.
    """

    @needs_local_scope
    @line_magic
    def require(self, line: str, local_ns=None):
        """Link required JS library.

        :param line: string in form '<key> <path>'
        :param local_ns: current cell namespace [optional]
        """
        user_ns = self.shell.user_ns
        user_ns.update(local_ns or dict())

        lib, path = line \
            .strip() \
            .split(sep=' ')

        return require(lib, path)

    @line_magic
    def link_css(self, line: str):
        """Link CSS stylesheet."""
        return link_css(line)

    @line_magic
    def link_js(self, line: str):
        """Link JavaScript library."""
        return link_js(line)

    @cell_magic
    def load_style(self, line: str, cell: str):
        """Create new style element and add it to the page."""
        attributes: dict = self._parse_attributes(line)

        return load_css(cell, attributes)

    @cell_magic
    def load_script(self, line: str, cell: str):
        """Create new script element and add it to the page."""
        attributes: dict = self._parse_attributes(line)

        return load_js(cell, attributes)

    @staticmethod
    def _parse_attributes(line: str) -> dict:
        """Parse string to return element attributes."""
        attr_def = map(
            lambda s: re.sub(r"[\"'](.*)[\"']", r"\1", s),
            line.split()
        )

        return {
            attr: val
            for attr, val in map(lambda s: s.split('='), attr_def)
        }
