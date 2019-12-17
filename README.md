jupyter-rs-vtk
===============================

VTK widget for Jupyter

Installation
------------

To install use pip:

    $ pip install .
    $ jupyter nbextension enable --py --sys-prefix jupyter_rs_vtk

To install for jupyterlab

    $ cd js
    $ jupyter labextension install .

For a development installation (requires npm),

    $ git clone https://github.com/radiasoft/rsjpyradia.git
    $ cd jupyter-rs-vtk
    $ pip install -e .
    $ jupyter nbextension install --py --symlink --sys-prefix jupyter_rs_vtk
    $ jupyter nbextension enable --py --sys-prefix jupyter_rs_vtk
