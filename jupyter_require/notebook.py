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

import csscompressor

from IPython import get_ipython

from .core import execute_with_requirements
from .core import safe_execute


Jupyter = get_ipython()
"""Current InteractiveShell instance."""


def link_css(href: str, attrs: dict = None):
    """Link CSS stylesheet."""
    script = """
        'use strict';
        
        const href = "$$href";
        const attributes = $$attrs || {};

        if ( !$(`link[href*="${href}"]`).length ) {
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
        }
    """

    return safe_execute(script, href=href, attrs=attrs)


def link_js(src: str):
    """Link JavaScript library."""
    script = """
        'use strict';

        const src = "$$src";
        
        if ( !$(`script[src*="${src}"]`) ) {
            let script = document.createElement("script");
            script.src = src;

            document.head.appendChild(script);
        }
    """

    return safe_execute(script, src=src)


def load_css(style: str, attrs: dict = None, compress=True, **compressor_options):
    """Create new style element and add it to the page."""
    attrs = attrs or {}

    script = """
        'use strict'
        
        const style = `$$style`;
        const attributes = $$attrs || {};
        
        let id = attributes.id;
        let elem_exists = id ? $(`style#${id}`).length > 0 : false;
        
        let e = elem_exists ? document.querySelector(`style#${id}`)
                            : document.createElement(\"style\");
        
        $(e).text(`${style}`).attr('type', 'text/css');
        
        Object.entries(attributes)
            .forEach( ([attr, val]) => $(e).attr(attr, val) );

        if (!elem_exists) document.head.appendChild(e);
    """

    if compress:
        style = csscompressor.compress(style, **compressor_options)

    return safe_execute(script, style=style, attrs=attrs)


def load_js(script: str, attrs: dict = None):
    """Create new script element and add it to the page."""
    attrs = attrs or {}

    # escape dollar signs inside ticks and ticks
    js = script \
        .replace('`', '\`') \
        .replace('${', '\${')

    script = """
        'use strict';
    
        const script = `$$js`;
        const attributes = $$attrs || {};
        
        let id = attributes.id;
        let elem_exists = id ? $(`script#${id}`).length > 0 : false;
        
        let e = elem_exists ? document.querySelector(`script#${id}`)
                            : document.createElement(\"script\");
        
        $(e).text(`${script}`).attr('type', 'text/javascript');
        
        Object.entries(attributes)
            .forEach( ([attr, val]) => $(e).attr(attr, val) );

        if (!elem_exists) document.head.appendChild(e);
    """

    return safe_execute(script, js=js, attrs=attrs)


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
