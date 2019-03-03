# jupyter-require

Jupyter magic library for managing linked JavaScript scripts and CSS styles.

# About

The [`jupyter-require`](https://github.com/CermakM/jupyter-require) library is intended to be used in [Jupyter] notebooks.

`jupyter-require` allows you to link custom [CSS] and [JavaScript] files
and even create and load your own styles and scripts directly from [Jupyter] notebook.

<br>

### What is this for?

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

> Note that the path does __NOT__ contain the `.js` file extension. This is [requireJS] standard.


The `%require` is _jupyter magic command_ and the rest are the parameters. The command takes lib name and path.


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


<br>
<hr>


[CSS]: https://www.w3schools.com/css/
[d3]: https://d3js.org
[JavaScript]: https://www.w3schools.com/js/default.asp
[Jupyter]: https://jupyter.org/
[RequireJS]: https://requirejs.org/


> Author: Marek Cermak <macermak@redhat.com> 
