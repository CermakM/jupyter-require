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

"""Common notebook utilities."""


from IPython import get_ipython

from .core import execute_with_requirements
from .core import safe_execute


Jupyter = get_ipython()
"""Current InteractiveShell instance."""


def enable_nbextension(nbextension):
    """Enable Jupyter nbextension."""
    script = """
    Jupyter.notebook.config.update({
        'load_extensions': {
            '$$nbextension': true
        }
    });
    """

    return safe_execute(script, nbextension=nbextension)


def disable_nbextension(nbextension):
    """Enable Jupyter nbextension."""
    script = """
    Jupyter.notebook.config.update({
        'load_extensions': {
            '$$nbextension': false
        }
    });
    """

    return safe_execute(script, nbextension=nbextension)


def load_nbextension(nbextension, endpoint: str = 'extension', enable=True):
    """Load Jupyter nbextension directly into the current notebook.

    Note: The extension has to be visible by notebook webserver, hence it has
    to be placed in defined folder locations (see the official [documentation])

    [documentation]: https://jupyter.readthedocs.io/en/latest/projects/jupyter-directories.html#jupyter-path
    """
    script = """
    utils.load_extensions('$$nbextension/$$endpoint');
    """

    if enable:
        enable_nbextension(nbextension)

    return execute_with_requirements(
        script, required=['base/js/utils'], nbextension=nbextension, endpoint=endpoint)


def clear_cell_metadata(index: int = None):
    """Clear cell requirement metadata."""
    script = """
    const index = $$index;
    
    let cells = Number.isInteger(index) ? [Jupyter.notebook.get_cell($$index)]
                                        : Jupyter.notebook.get_cells();
    
    cells.forEach((d, i) => {
        if (d.metadata.hasOwnProperty('require')) delete d.metadata.require;
    });
    """

    return safe_execute(script, index=index)


def clear_notebook_metadata():
    """Clear notebook requirement metadata."""
    script = """
    let nb = Jupyter.notebook;
    
    if (nb.metadata.hasOwnProperty('require')) delete nb.metadata.require;
    """

    return safe_execute(script)
