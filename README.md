# jupyter-require

Jupyter nbextension for JavaScript execution and managing linked libraries and CSS stylesheets in Jupyter notebooks.

# About

The [`jupyter-require`](https://github.com/CermakM/jupyter-require) library is intended to be used in [Jupyter] notebooks.

and even create and load your own styles and scripts directly from [Jupyter] notebook.
Jupyter-require allows to execute and manage custom [JavaScript] and [CSS] files and even create and load your own styles and scripts directly from [Jupyter] notebook.

Jupyter-require provides unique opportunity to customize Jupyter notebooks and enables users to handcraft their own JavaScript-augmented workflows while keeping in mind synchronicity demands and security implications of such approaches.

<br>

### What is this for?

Let's demonstrate the usage on an example. Note that the usage is limited only by your imagination, this is just a demonstration of a single use case.

<br>

If you are into data visualization like me, you've most likely already heard of [d3].js JavaScript ecosystem.
It's incredibly powerful tool which can be used to create advanced interactive visualizations.

However, it is not very comfortable to use in Jupyter notebooks let alone integrate with Python
(see the article about [Custom D3.js Visualization in a Jupyter Notebook](https://www.stefaanlippens.net/jupyter-custom-d3-visualization.html)).

That's where `jupyter-require` and related [`jupyter-d3`](https://github.com/CermakM/jupyter-d3) come into play.
`jupyter-require` allows you to source custom scripts (like [d3]) and styles and use them within the notebook with ease.


Check out also [`jupyter-d3`](https://github.com/CermakM/jupyter-d3) which takes the [d3] workflow
 in Jupyter notebooks to another level.

<br>

# Installation

<br>

`pip install jupyter-require`

To install the nbextension and enable it, we have supplied a helper functions in the `utils` module.

```Python
from jupyter_require.utils import utils

# install jupyter-require extension
utils.install_nbextension('jupyter_require', overwrite=True)  # note there is an underscore, it's Python module name

# load and enable the extension
utils._load_nbextension(enable=True)
```

All of that above can be done from command line, so if you're used to install nbextensions the regular way, feel free to do so. In fact, you are **recommended** to, this approach is just for lazy people like myself.

> NOTE: You may need to reload the page (just hit F5) after these steps for the jupyter-require nbextension to initialize properly.

# Example usage

In [Jupyter] notebooks:

```python
%load_ext jupyter_require
```

### Loading libraries

Loading required libraries is now as simple as:

```python
%require d3 https://d3js.org/d3.v5.min
%require d3-hierarchy https://d3js.org/d3-hierarchy.v1.min
```

> Note that the path does **NOT** contain the `.js` file extension. This is [requireJS] standard.


The `%require` is *jupyter magic command* and the rest are the parameters. The command takes lib name and path.


### Creating custom style elements

```css
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
```

If you're not a fan of magic commands, you can make use of equivalent API calls.

```python
from jupyter_require import require
from jupyter_require import load_css

require.config({
  'd3': 'https://d3js.org/d3.v5.min'
  'd3-hierarchy': 'https://d3js.org/d3-hierarchy.v1.min'
})

load_css(...)  # stylesheet goes here
```

<br>

Now we can actually make use of the bidirectional communication between Python and JS

Let's say we have the following [d3] script:

> Note: I assume that we work in Jupyter notebook environment and hence we have the context cell at our disposal.


```javascript
/**
 * @module
 * @description  Print coloured circles into the cell output
 * @file  d3-simple-example.js
 */

 // Inspired by: https://www.d3-graph-gallery.com/intro_d3js.html

// create SVG element in the output area
// the `element` is a contextual binding to the output of the current cell
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
```

Now in order to execute the script in a cell, we will have to tell it to use the [d3]. The `execute_with_requirements` is made exactly for that purpose.

```python
from pathlib import Path
from jupyter_require import execute_with_requirements

script = Path('d3-simple-example.js').read_text()

execute_with_requirements(script, required=['d3'])
```

<div class='output' id="d3-simple-example-output">
<svg><g><circle cx="2" cy="2" r="40" style="fill: blue;"></circle><circle cx="140" cy="70" r="40" style="fill: red;"></circle><circle cx="300" cy="100" r="40" style="fill: green;"></circle></g></svg>
</div>


And you should see those three pretty circles :point_up: .

> NOTE: It is possible that the current markdown renderer does not render the raw `</svg>` element above, all the more reason to try it yourself! :smirk:

<br>

There is certainly more to it, but I am gonna leave it to your adventurous desires.

<br>

# Synchronicity

JavaScript execution is by default asynchronous. All the more in Jupyter notebooks.
Executing custom JavaScript script will happen asynchronously and the rest of the notebook won't wait for the execution to complete.

This is very often not a desired behavior, since we might to work with the results of the execution in the next cell.

Jupyter-require solves this issue by converting every executed script into [`Promise`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise) and awaiting it while pausing the execution of Python kernel.

<br>

# Execution & Security -- *safe scripts* and *finalization*

In Jupyter notebooks, it might be sometimes unfortunate how the JavaScript is stored (and treated) in general in the notebook environment.
`jupyter-require` introduces the notion of *safe scripts* and *finalization*. Let's look at the latter first.

**Finalization**

When user executes a script via native Jupyter API, that is typicaly something like `display(Javascript("""..."""))`, what happens behind the scenes is actually quite complicated. The one important thing to now, however, is that the *whole* script is embedded into the cell output and the resulting `*.ipynb` file.
Then, **every time** a cell is copied or re-created (i.e., on notebook reload), the script is **executed**. Since this execution is not sand-boxed. In fact, it is executed in **window context** using `eval` function (see the section ['Do not ever use`eval`!'](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/eval#Do_not_ever_use_eval!) from the official [MDN web docs]).
This can potentially be a security threat!
Also, if you don't want to share the script that produced the output, but you want the output to be present, this does not happen either.

We try to combat that issue step by step, our approach is not optimal either, but it does yield some improvements and we believe that over time, it will get even better. When executing script *with* jupyter-require `execute_with_requirements` function, it is not the script which is embedded, it is the **Function object** itself which the cells carries with. This allows the script to be re-executed when we copy/paste a cell or stored in a clipboard when cutting the cell.
Also, we do not evaluate the script in window context using the `eval` function, as Jupyter by default does. Instead, at the current development state, we **wrap it** in its own **Function scope** and set its `this` and `element` context manually.

Aight, still not a word about *finalization*, right? What finalization means in this context, is **discarding** the JavaScript code which produced the output, cleaning the metadata and **saving the output** displayed in the cell output area into static state.
Going back to the [d3] example, finalizing the cells would make the plot that we produced persistent and JSON serializable. The output would then be visible in tools like [nbviewer] or [GitHub] `ipynb` preview.

> NOTE: SVG do pose another security issue, however, hence GitHub might not display them to prevent that, see for example [this](https://github.community/t5/How-to-use-Git-and-GitHub/Embedding-a-SVG/td-p/2192) conversation. We will try to act on this issue in the future.

We are thinking about the ways we could sand-box the execution and the output even more, but bare in mind that this project is very young, so let's put one foot in front of the other.

To finalize your outputs, use the `Save and Finalize` action button which should be present on the right of the regular `Save and Checkpoint` button. The finalization also happens automaticaly when you *properly* close the notebook. We cannot handle SIGTERMs at the moment, so be aware that in that case the scripts will be discarded and the output lost.

<br>

**Safe scripts**

> ⚠️ The notion of safe scripts is something which has been added pretty recently and is under heavy observation.

By the word _safe_ we don't refer to an execution which reduces security threats, no, nothing like that. It is *YOU* who guaratee that the script *is* safe and can be treated as such.
The mechanism which we treat *safe scripts* by is very similar to the one described above, with one important change: safe scripts are similar to the default Jupyter notebook behaviour in a sense that hey are also **executed on the notebook reload** and are also **stored in the resulting `*.ipynb` notebook file**.

Hence you can enjoy the benefits of sand-box(ish) synchronous execution while still having the scripts stored in the output. The one **limitation** is that they do not allow to specify requirements as the `execute_with_requirements` function does by its `required` parameter. This is becouse those scripts can be executed *before* extensions are actually loaded and we can not guarantee (at least we don't know how, right now) that the funcionality of jupyter-require will be present at that time.

To treat your script as *safe script*, execute it with `safe_execute` function.


<br>
<hr>


[CSS]: https://www.w3schools.com/css/
[d3]: https://d3js.org
[GitHub]: https://github.com/
[JavaScript]: https://www.w3schools.com/js/default.asp
[Jupyter]: https://jupyter.org/
[nbviewer]: https://nbviewer.jupyter.org/
[MDN web docs]: https://developer.mozilla.org/en-US/
[RequireJS]: https://requirejs.org/


> Author: Marek Cermak <macermak@redhat.com>
