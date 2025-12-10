
Installation
============

User Installation
-----------------
You can install Melodie via `pip`:

.. code-block:: shell

   pip install Melodie


Developer Installation
----------------------
To contribute to Melodie, first clone the repository and set up an editable
install using pip.

.. code-block:: shell

   git clone git@github.com:ABM4ALL/Melodie.git
   cd Melodie

   # Create and activate a virtual environment (recommended)
   python -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`

   # Install in editable mode. This also installs all required dependencies.
   pip install -e .

To rebuild the Cython binary extensions in-place after making changes, run:

.. code-block:: shell

   # Build the Cython packages
   python setup.py build_ext -i

   # Run pytest to verify the installation and check your changes.
   pytest


To build documentation locally, use the following commands:

.. code-block:: shell

   # Install doc build requirements
   pip install -r docs/requirements.txt

   # Build docs
   cd docs
   make html

   # Or, for live-reloading as you edit:
   # sphinx-autobuild source ../_build/html -E -a


To keep local repository up to date, please follow these steps:

.. code-block:: shell

   git pull origin <branch-name>

   # Re-build Cython packages
   python setup.py build_ext -i

   # Test the installation
   pytest

Dependency Note
---------------
Melodie's core functionality relies on several key packages:

* Python 3.8+
* numpy
* pandas
* matplotlib
* scikit-opt
* networkx
* sqlalchemy (Database connection)
* rpyc (Parallel computing)
* flask (Web interface)

Python versions 3.8 through 3.14 are tested and supported.

For detailed dependencies, please visit
`requirements.txt <https://github.com/ABM4ALL/Melodie/blob/master/requirements.txt>`_

