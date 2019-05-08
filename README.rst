***************
jupyter-require
***************

Jupyter nbextension for JavaScript execution and managing linked libraries and CSS stylesheets in Jupyter notebooks.

|

About
=====

The `jupyter-require`_ library is intended to be used in `Jupyter`_ notebooks.

Jupyter-require allows to execute and manage custom `JavaScript`_ and `CSS`_ files and even create and load your own styles and scripts directly from `Jupyter`_ notebook.

Jupyter-require provides a unique opportunity to customize Jupyter notebooks and enables users to handcraft their own JavaScript-augmented workflows while keeping in mind synchronicity demands and security implications of such approaches.

|

What is this for?
=================

Let's demonstrate the usage on an example. Note that the usage is limited only by your imagination, this is just a demonstration of a single use case.

|

If you are into data visualization like me, you've most likely already heard of `d3`_.js JavaScript ecosystem.
It's an incredibly powerful tool which can be used to create advanced interactive visualizations.

However, it is not very comfortable to use in Jupyter notebooks let alone integrate with Python.

    See the article about `Custom D3.js Visualization in a Jupyter Notebook <https://www.stefaanlippens.net/jupyter-custom-d3-visualization.html>`_.


|


That's where `jupyter-require`_ and related `jupyter-d3`_ come into play.
jupyter-require allows you to source custom scripts (like `d3`_) and styles and use them within the notebook with ease.


Check out also `jupyter-d3`_ which takes the `d3`_ workflow in Jupyter notebooks to another level.

|

Installation
============

To install jupyter-require Python package:


.. code-block:: bash

    pip install jupyter-require


And to install the nbextension itself and enable it, we have supplied a helper functions in the `jupyter-nbutils <https://github.com/CermakM/jupyter-nbutils>`_ ``utils`` module.


.. code-block:: python

    from jupyter_nbutils import utils

    # install jupyter-require extension
    utils.install_nbextension('jupyter_require', overwrite=True)  # note there is an underscore, it's Python module name

    # load and enable the extension
    utils.load_nbextension('jupyter-require', enable=True)


All of that above can be done from command line, so if you're used to installing nbextensions the regular way, feel free to do so. In fact, you are **recommended** to, this approach is just for lazy people like myself.

    NOTE: You may need to reload the page (just hit F5) after these steps for the jupyter-require nbextension to initialize properly.

|

Example usage
=============

In `Jupyter`_ notebooks:

.. code-block:: python

    %load_ext jupyter_require


Loading libraries
-----------------

Loading required libraries is now as simple as:

.. code-block:: python

    %require d3 https://d3js.org/d3.v5.min
    %require d3-hierarchy https://d3js.org/d3-hierarchy.v1.min

    NOTE: Note that the path does **NOT** contain the `.js` file extension. This is `requireJS`_ standard.


The ``%require`` is *jupyter magic command* and the rest are the parameters. The command takes a lib name and path.


Creating custom style elements
------------------------------

.. code-block: css

    %%load_css

    /* d3.css */


    .links text {
        fill: none;
        stroke: #ccc;
        stroke-width: 1px;

    }

    .nodes {
        z-index: 1;
        font: 13px sans-serif;
    }

    .nodes circle {
        fill: darkslateblue;
        stroke: none;
    }

If you're not a fan of magic commands, you can make use of equivalent API calls.

.. code-block:: python

    from jupyter_require import require
    from jupyter_require import load_css

    require.config({
      'd3': 'https://d3js.org/d3.v5.min'
      'd3-hierarchy': 'https://d3js.org/d3-hierarchy.v1.min'
    })

    load_css(...)  # stylesheet goes here

|

Executing custom script
-----------------------

Now we can actually make use of the bidirectional communication between Python and JS

Let's say we have the following `d3`_ script:

    NOTE: I assume that we work in Jupyter notebook environment and hence we have the context cell at our disposal.


.. code-block:: javascript

    /**
     * @module
     * @description  Print coloured circles into the cell output
     * @file  d3-simple-example.js
     */

     // Inspired by: https://www.d3-graph-gallery.com/intro_d3js.html

    // create SVG element in the output area
    // the ``element`` is a contextual binding to the output of the current cell
    let svg = d3.select(element.get(0))
      .append('svg');

    // create group
    let g = svg.append('g');

    g.append("circle")
      .attr("cx", 2).attr("cy", 2).attr("r", 40).style("fill", "blue");
    g.append("circle")
      .attr("cx", 140).attr("cy", 70).attr("r", 40).style("fill", "red");
    g.append("circle")
      .attr("cx", 300).attr("cy", 100).attr("r", 40).style("fill", "green");


Now in order to execute the script in a cell, we will have to tell it to use the `d3`_. The ``execute_with_requirements`` is made exactly for that purpose.

.. code-block:: python

    from pathlib import Path
    from jupyter_require import execute_with_requirements

    script = Path('d3-simple-example.js').read_text()

    execute_with_requirements(script, required=['d3'])

.. image:: ./docs/images/readme_example.svg
    :align: center
    :alt: SVG Example generated by d3
    :target: https://github.com/CermakM/jupyter-require/blob/master/docs/images/readme_example.svg

And you should see those three pretty circles :point_up: .

    ⚠️ It is possible that the current markdown renderer does not render the raw `</svg>` element above, all the more reason to try it yourself! :smirk:

|

There is certainly more to it, but I am gonna leave it to your adventurous desires.

|

Synchronicity
=============

JavaScript execution is by default asynchronous. All the more in Jupyter notebooks.
Executing custom JavaScript script will happen asynchronously and the rest of the notebook won't wait for the execution to complete.

This is very often not the desired behaviour, since we might to work with the results of the execution in the next cell.

Jupyter-require solves this issue by converting every executed script into `Promise <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise>`__ and awaiting it while pausing the execution of Python kernel.

|

Execution & Security -- *safe scripts* and *finalization*
=========================================================

In Jupyter notebooks, it might be sometimes unfortunate how the JavaScript is stored (and treated) in general in the notebook environment.
``jupyter-require`` introduces the notion of *safe scripts* and *finalization*. Let's look at the latter first.

**Finalization**

When a user executes a script via native Jupyter API, that is typically something like ``display(Javascript("""..."""))``, what happens behind the scenes is actually quite complicated. The one important thing to now, however, is that the *whole* script is embedded into the cell output and the resulting `*.ipynb` file.
Then, **every time** a cell is copied or re-created (i.e., on notebook reload), the script is **executed**. Since this execution is not sandboxed. In fact, it is executed in **window context** using ``eval`` function.

    See: The section `'Do not ever use eval!' <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/eval#Do_not_ever_use_eval!>`_ from the official `MDN web docs`_).

This can potentially be a security threat!
Also, if you don't want to share the script that produced the output, but you want the output to be present, this does not happen either.

We try to combat that issue step by step, our approach is not optimal either, but it does yield some improvements and we believe that over time, it will get even better. When executing script *with* jupyter-require ``execute_with_requirements`` function, it is not the script which is embedded, it is the **Function object** itself which the cells carry with. This allows the script to be re-executed when we copy/paste a cell or stored in a clipboard when cutting the cell.

Also, we do not evaluate the script in window context using the ``eval`` function, as Jupyter by default does. Instead, at the current development state, we **wrap it** in its own **Function scope** and set its ``this`` and ``element`` context manually.

Aight, still not a word about *finalization*, right? What finalization means in this context, is **discarding** the JavaScript code which produced the output, cleaning the metadata and **saving the output** displayed in the cell output area into a static state.
Going back to the `d3`_ example, finalizing the cells would make the plot that we produced persistent and JSON serializable. The output would then be visible in tools like `nbviewer`_ or `GitHub`_ ``ipynb`` preview.

    ⚠️ SVG poses another security issue, however, hence GitHub might not display them to prevent that, see for example `this <https://github.community/t5/How-to-use-Git-and-GitHub/Embedding-a-SVG/td-p/2192>`_ conversation. We will try to act on this issue in the future.


|

We are thinking about the ways we could sandbox the execution and the output even more, but bare in mind that this project is very young, so let's put one foot in front of the other.

To finalize your outputs, use the ``Save and Finalize`` action button which should be present on the right of the regular ``Save and Checkpoint`` button. The finalization also happens automatically when you *properly* close the notebook. We cannot handle SIGTERMs at the moment, so be aware that in that case the scripts will be discarded and the output lost.

|

**Safe scripts**

    ⚠️ The notion of safe scripts is something which has been added pretty recently and is under heavy observation.

By the word *safe* we don't refer to an execution which reduces security threats, no, nothing like that. It is *YOU* who guarantee that the script *is* safe and can be treated as such.
The mechanism which we treat *safe scripts* by is very similar to the one described above, with one important change: safe scripts are similar to the default Jupyter notebook behaviour in a sense that they are also **executed on the notebook reload** and are also **stored in the resulting `*.ipynb` notebook file**.

Hence you can enjoy the benefits of a sandbox(ish) synchronous execution while still having the scripts stored in the output. The one **limitation** is that they do not allow to specify requirements as the ``execute_with_requirements`` function does by its ``required`` parameter. This is because those scripts can be executed *before* extensions are actually loaded and we can not guarantee (at least we don't know how right now) that the functionality of jupyter-require will be present at that time.

To treat your script as *safe script*, execute it with ``safe_execute`` function.


|

.. _jupyter-require:    https://github.com/CermakM/jupyter-require
.. _jupyter-d3:         https://github.com/CermakM/jupyter-d3
.. _CSS:                https://www.w3schools.com/css/
.. _d3:                 https://d3js.org
.. _GitHub:             https://github.com/
.. _JavaScript:         https://www.w3schools.com/js/default.asp
.. _Jupyter:            https://jupyter.org/
.. _nbviewer:           https://nbviewer.jupyter.org/
.. _MDN web docs:       https://developer.mozilla.org/en-US/
.. _RequireJS:          https://requirejs.org/

|

----

.. rubric:: Footnotes

+-------------------+------------------------------------------------+
| resource          | link                                           |
+===================+================================================+
| jupyter-require   | `https://github.com/CermakM/jupyter-require`   |
+-------------------+------------------------------------------------+
| jupyter-d3        | `https://github.com/CermakM/jupyter-d3`        |
+-------------------+------------------------------------------------+
| CSS               | `https://www.w3schools.com/css/`               |
+-------------------+------------------------------------------------+
| D3                | `https://d3js.org`                             |
+-------------------+------------------------------------------------+
| GitHub            | `https://github.com/`                          |
+-------------------+------------------------------------------------+
| JavaScript        | `https://www.w3schools.com/js/default.asp`     |
+-------------------+------------------------------------------------+
| Jupyter           | `https://jupyter.org/`                         |
+-------------------+------------------------------------------------+
| nbviewer          | `https://nbviewer.jupyter.org/`                |
+-------------------+------------------------------------------------+
| MDN web docs      | `https://developer.mozilla.org/en-US/`         |
+-------------------+------------------------------------------------+
| requireJS         | `https://requirejs.org/`                       |
+-------------------+------------------------------------------------+

|

    Author: Marek Cermak <macermak@redhat.com>
