
Contribution
============

Report Bugs
___________

Feel free to report bugs at https://github.com/ABM4ALL/Melodie/issues.

Report Melodie Bugs
~~~~~~~~~~~~~~~~~~~

The bug report should contain these information below:

* System information, including

    * Version of Melodie.
    * Operating system.
    * Python version and the architecture of python executable. The architecture of python executable **MAY NOT** be the same as the architecture of your computer, especially if you are using an Apple Computer with M1 chip.
    * Version of Cython, Numpy and any other third-party packages that you think is vital to reproduce this bug.

* Steps to reproduce the bug.
* Any other things that you think might be helpful for troubleshooting.

If Melodie has been successfully installed, you can also gather the system information within one command ``python -m Melodie info``:

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

Just copy & paste the information into the issue.
If this command fails, we are sorry that you have to gather the information manually,
and this `link <https://github.com/ABM4ALL/Melodie/blob/master/Melodie/tools/system_info.py>`_ might be helpful.

Report Documentation Bugs
~~~~~~~~~~~~~~~~~~~~~~~~~

System information is not necessary for documentation bugs,
feel free to post a new issue with just a screenshot containing the bug.

Ask for Functionalities
_______________________

If you need functionalities that has not been implemented yet,
feel free to suggest new features by creating new issues.

How to Contribute
_________________

If you have idea in fixing bugs or adding new features, you could make your own contribution.

Here is the guide:

* Fork the Melodie repository on GitHub: https://github.com/ABM4ALL/Melodie.
* Install with the developer installation.
* Make your changes locally.
* Run pytest command to test the changes.
* Push to your repo, and submit a pull-request on GitHub.

Besides, we are also happy if you would like to publish your model developed with **Melodie** on ABM4ALL.
At the same time, welcome to add a page for your model in the :ref:`Model Gallery` section.
