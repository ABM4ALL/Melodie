
Installation
============

User Installation
-----------------
You can install Melodie via `pip`:

.. code-block:: shell

   pip install Melodie


Developer Installation
----------------------
To install for development, first clone the repository and then install
via pip's development mode.

.. code-block:: shell

   git clone git@github.com:ABM4ALL/Melodie.git
   cd Melodie

   # Install the requirements
   pip install -r build_requirements.txt
   pip install -r requirements.txt

   pip3 install -e .

To build with developing mode and build binary extensions in place, use the following commands:

.. code-block:: shell

   # Build the Cython packages
   python setup.py build_ext -i

   # Run pytest to check if the installation finished successfully.
   pytest


To build documentation locally, use the following commands:

.. code-block:: shell

   # Build docs
   cd docs
   sphinx-autobuild source html -E -a


To keep local repository up to date, please follow these steps:

.. code-block:: shell

   git pull origin <branch-name>

   # Re-build Cython packages
   python setup.py build_ext -i

   # Test the installation
   pytest

Dependency Note
---------------
The dependencies that related to functionalities of Melodie are listed below.

* Python >=3.8
* numpy
* pandas
* matplotlib
* scikit-opt
* networkx

For detailed dependencies, please visit
`requirements.txt <https://github.com/ABM4ALL/Melodie/blob/master/requirements.txt>`_
and
`build_requirements.txt <https://github.com/ABM4ALL/Melodie/blob/master/build_requirements.txt>`_

