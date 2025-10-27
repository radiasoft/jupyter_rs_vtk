# jupyter_rs_vtk

VTK widget for Jupyter

## Installation

For a development installation (requires [Node.js](https://nodejs.org) and [Yarn version 1](https://classic.yarnpkg.com/)),

    $ git clone https://github.com/RadiaSoft LLC/jupyter_rs_vtk.git
    $ cd jupyter_rs_vtk
    $ pip install -e .
    $ cd js
    $ jupyter labextension install --no-build .
    $ NODE_OPTIONS="--openssl-legacy-provider" jupyter lab build
