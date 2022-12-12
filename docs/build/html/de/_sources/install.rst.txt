.. Melodie documentation installation instructions.

.. _installation:

Installation
============

User Installation
-----------------
You can install Melodie via `pip`:

.. code-block::

   pip install Melodie


Developer Installation
----------------------
To install Melodie for development, first clone the repository and then install
via pip's development mode.

.. code-block::

   git clone git@github.com:SongminYu/Melodie.git
   cd Melodie
   pip install -r requirements.txt
   pip install -e . --no-deps


.. WARNING::
   If you are using `conda` to manage your virtual environment, then you must also
   install ffmpeg.


Dependency Note
---------------
Melodie has the following dependencies

* Python 3.7 or Python3.8
* numpy
* pandas
* matplotlib
