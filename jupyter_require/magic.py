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

from jupyter_nbutils.utils import sanitize_namespace

from .core import execute_with_requirements
from .core import require as requirejs
from .core import safe_execute

from .core import JSTemplate

from .notebook import link_css
from .notebook import link_js
from .notebook import load_js
from .notebook import load_css


def activate_js_syntax_highlight(regex: str = 'require'):
    """Activates syntax highlighting for the `%%require` cells."""
    script = """
      codecell.CodeCell.options_default.highlight_modes['magic_text/javascript'] = {'reg':[/^%%$$regex/]};
      
      Jupyter.notebook.events.one('kernel_ready.Kernel', function(){
          Jupyter.notebook.get_cells().map(function(cell){
              if (cell.cell_type == 'code'){ cell.auto_highlight(); } }) ;
      });
      
      console.debug("JavaScript syntax highlight activated for '%%$$regex'.");
    """
    
    return execute_with_requirements(script, required=['notebook/js/codecell'], regex=regex)


@magics_class
class RequireJSMagic(Magics):
    """Ipython magic for RequireJS class.

    Links JavaScript libraries to Jupyter Notebook.
    """

    def __init__(self, *args, **kwargs):
        super(RequireJSMagic, self).__init__(*args, **kwargs)

        activate_js_syntax_highlight()

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

        return requirejs(lib, path)

    @needs_local_scope
    @cell_magic
    def require(self, line: str, cell: str, local_ns=None):
        """Execute current JS cell with requirements.

        The required libraries specified in parameters have to be defined and loaded in advance. `require` line magic can be used for that purpose.

        :param line: str, requirements separated by spaces
        :param cell: str, script to be executed
        :param local_ns: current cell namespace [optional]
        """
        user_ns = self.shell.user_ns
        user_ns.update(local_ns or dict())

        ns = sanitize_namespace(user_ns, options={'warnings': False})

        # do not use safe substitution here
        script = JSTemplate(cell).substitute(**ns)

        required = line \
            .strip() \
            .split(sep=' ')

        return execute_with_requirements(script, required)

    @cell_magic
    def define(self, line: str, cell: str):
        """Define new module from the current cell content.
        
        :param line: module name
        :param cell: script to be defined as module by the module name
        """
        if not line:
            raise ValueError("Module name required but not provided.")

        script = """
        const module = '$$module';

        // overwrite any previously defined modules with the same name
        requirejs.undef(module);

        define(module, function(require) {
            $$cell
        });
        """

        return safe_execute(script, cell=cell, module=line)

    @line_magic
    def undef(self, line: str):
        """Undefine required libraries.

        :param line: str, libs to undefine separated by spaces
        """
        libs = line \
            .strip() \
            .split(sep=' ')

        script = """
            const libs = $$to_undefine;

            libs.forEach((lib) => {
                requirejs.undef(lib);
            });
        """

        for lib in libs:
            requirejs.pop(lib)

        return safe_execute(script, to_undefine=libs)

    @line_magic
    def reload(self, line: str):
        """Reload libraries.

        This is especially useful when needed to reload
        script after making changes to it.

        :param line: str, libs to reload separated by spaces
        """
        libs = line \
            .strip() \
            .split(sep=' ')

        script = """
            const libs = $$to_reload;

            libs.forEach((lib) => {
                requirejs.undef(lib);
            });
            requirejs(libs, () => {
                console.debug(`Libraries ${libs} reloaded.`);
            });
        """

        return safe_execute(script, to_reload=libs)

    @line_magic
    def link_css(self, line: str):
        """Link CSS stylesheet."""
        return link_css(line)

    @line_magic
    def link_js(self, line: str):
        """Link JavaScript library."""
        return link_js(line)

    @cell_magic
    def load_css(self, line: str, cell: str):
        """Create new style element and add it to the page."""
        attributes: dict = self._parse_attributes(line)

        return load_css(cell, attributes)

    @cell_magic
    def load_js(self, line: str, cell: str):
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
