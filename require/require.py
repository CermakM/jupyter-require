# jupyter-d3
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

"""Module for managing linked JavaScript Libraries via requireJS."""

from string import Template
from textwrap import dedent
from traitlets import Dict, HasTraits, observe, Unicode

from IPython.core.display import display, Javascript


_REQUIREJS_TEMPLATE = Template(dedent("""
    'use strict';
    
    require.config({
        paths: {
            $libs
        }
    });
"""))


class RequireJS(HasTraits):

    _LIBS = Dict(Unicode(allow_none=False), default_value=dict(), help="""
        Linked JavaScript libraries.
    """)

    @observe('_LIBS')
    def update(self, *args):
        """Update requireJS config in Jupyter Notebook."""
        # required libraries
        libs = (
            f"'{key}': '{path}'" for key, path in self._LIBS.items()
        )
        require_js: str = _REQUIREJS_TEMPLATE.safe_substitute(
            libs=', '.join(libs))

        return display(Javascript(dedent(require_js)))

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
        self._LIBS['library'] = path

    def config(self, libs: dict):
        """Links JavaScript libraries to Jupyter Notebook.

        The libraries are linked using requireJS such as:

        ```javascript
        require.config({ paths: {<key>: <path>} });
        ```

        Please note that <path> does __NOT__ contain `.js` suffix.
        """
        self._LIBS = libs

    @property
    def loaded_libraries(self) -> dict:
        """Get loaded libraries."""
        return dict(self._LIBS)


def link_css(stylesheet: str):
    """Link CSS stylesheet."""
    script = (
        "'use strict';"
        
        f"const href = \"{stylesheet}\";"
        """
        var link = document.createElement("link");
        link.rel = "stylesheet";
        link.type = "text/css";
        link.href = href;

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
        var script = document.createElement("script");
        script.src = src;

        document.head.appendChild(script);
        """
    )

    return display(Javascript(script))


def load_style(style: str, attrs: dict):
    """Create new style element and add it to the page."""
    script = (
        "'use strict';"
        
        f"const style = `{style}`;"
        f"const attributes = {attrs};"
        """
        let id = attributes.id;
        let elem_exists = id ? $(`style#${id}`).length > 0 : false;
        
        var e = elem_exists ? document.querySelector(`style#${id}`)
                            : document.createElement(\"style\");
        
        $(e).text(`${style}`).attr('type', 'text/css');
        
        Object.entries(attributes)
            .forEach( ([attr, val]) => $(e).attr(attr, val) );

        if (!elem_exists) document.head.appendChild(e);
        """
    )

    return display(Javascript(script))


def load_script(script: str, attrs: dict):
    """Create new script element and add it to the page."""
    script = (
        "'use strict';"
        
        f"const script = `{script}`;"
        f"const attributes = {attrs};"
        """
        let id = attributes.id;
        let elem_exists = id ? $(`script#${id}`).length > 0 : false;
        
        var e = elem_exists ? document.querySelector(`script#${id}`)
                            : document.createElement(\"script\");
        
        $(e).text(`${script}`).attr('type', 'text/css');
        
        Object.entries(attributes)
            .forEach( ([attr, val]) => $(e).attr(attr, val) );

        if (!elem_exists) document.head.appendChild(e);
        """
    )

    return display(Javascript(script))

