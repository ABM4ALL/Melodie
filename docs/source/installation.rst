.. Melodie documentation installation instructions.

.. installation:

Installation
============

User Installation
-----------------
You can install Melodie via `pip`:

.. code-block:: shell

   pip install Melodie
   pip install MelodieStudio


Developer Installation
----------------------
To install Melodie for development, first clone the repository and then install
via pip's development mode.

.. code-block:: shell

   git clone git@github.com:SongminYu/Melodie.git
   cd Melodie

   # Install the requirements
   pip install -r build_requirements.txt
   pip install -r requirements.txt

   # Build the Cython packages
   python setup.py build_ext -i
   # Run pytest to check if the installation finished successfully.
   pytest

To keep your local repository up to date, please follow these steps below:

.. code-block:: shell

   git pull origin <branch-name>
   # Re-build Cython packages
   python setup.py build_ext -i

   # Test the installation
   pytest

Dependency Note
---------------
The dependencies that related to functionalities of Melodie are listed below.

* Python >=3.7
* numpy
* pandas
* matplotlib
* scikit-opt
* networkx

For detailed dependencies, please visit
`requirements.txt <https://github.com/SongminYu/Melodie/blob/master/requirements.txt>`_
and
`build_requirements.txt <https://github.com/SongminYu/Melodie/blob/master/build_requirements.txt>`_

