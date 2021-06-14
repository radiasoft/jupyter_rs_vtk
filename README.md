jupyter-rs-vtk
===============================

VTK widget for Jupyter

Installation
------------

To install use pip:

    $ pip install .
    $ jupyter nbextension install --py --symlink --sys-prefix jupyter_rs_vtk
    $ jupyter nbextension enable --py --sys-prefix jupyter_rs_vtk

To install for jupyterlab

    $ jupyter labextension install js

For a development installation (requires npm),

    $ git clone https://github.com/radiasoft/jupyter-rs-vtk.git
    $ cd jupyter-rs-vtk
    $ pip install -e .
    $ jupyter nbextension install --py --symlink --sys-prefix jupyter_rs_vtk
    $ jupyter nbextension enable --py --sys-prefix jupyter_rs_vtk
    $ jupyter labextension install js
