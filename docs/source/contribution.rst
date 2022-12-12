
Contribution
============

<Words for pleasantries>

Report Bugs
---------------
Feel free to report bugs at https://github.com/SongminYu/Melodie/issues.

Report Melodie Bugs
^^^^^^^^^^^^^^^^
The bug report should contain these information below:

* System information

    * Version of Melodie
    * Operating system
    * Python version and the architecture of python executable. The architecture of python executable **MAY NOT** be the same as the architecture of your computer, especially
      if you are using a Apple Computer with M1 chip.
    * Version of Cython, Numpy and any other third-party packages that you think is vital to reproduce this bug.
* Steps to reproduce the bug.
* Any other things that you think might be helpful in troubleshooting.

If Melodie has been successfully installed, just gather the system information within one command:

.. code-block:: shell

    python -m Melodie info


The result is:

.. code-block:: text

    awesome-researcher@loyal-computer goodproject % python -m Melodie info

    Here is the information for Melodie
    ===================================
    Melodie Version  :  0.1.0
    Python Version   :  3.8.12
    Python Arch      :  ('64bit', '')
    Platform Detail  :  macOS-10.16-x86_64-i386-64bit
    Cython Version   :  3.0.0a10
    Numpy Version    :  1.21.5

Just copy & paste the result into the issue. However, if this command fails, we are sorry that you have to gather the information
manually. If you are not familiar with how to collect the information, the
`interals of "Melodie info" command <https://github.com/SongminYu/Melodie/blob/master/Melodie/tools/system_info.py>`_
may provide you a solution.

Report documentation bugs
^^^^^^^^^^^^^^^^
System information is unnecessary for documentation bugs, feel free to post a new issue with just a screenshot containing bugs.


Ask for Functionalities
^^^^^^^^^^^^^^^^
If you need functionalities that has not been implemented yet, feel free to suggest features that need to be integrated in a new issue.

How to contribute
---------------------
If you have idea in fixing bugs or adding new features, you could make your own contribution. Here is the guide:

* Fork the Melodie repository on GitHub: https://github.com/SongminYu/Melodie
* Install with the developer installation.
* Make your changes locally.
* Run pytest command to test the changes
* Push to your repo, and submit a pull-request on GitHub.
