
Contribution
============

We warmly welcome contributions to the Melodie project! Whether it's reporting a bug, suggesting a new feature, or submitting code, your help is valuable. This guide outlines how you can contribute effectively.

Reporting Issues
----------------

If you encounter a bug, have a question, or want to suggest an enhancement, the best place to do so is on the `GitHub Issues page <https://github.com/ABM4ALL/Melodie/issues>`_.

**Bug Reports**

A well-documented bug report helps us diagnose and fix problems faster. Please include the following:

1.  **System Information**: Melodie provides a command to gather essential system details. Please run it in your terminal and include the output in your report:

    .. code-block:: bash

       python -m Melodie info

2.  **Steps to Reproduce**: Provide a clear, step-by-step description of how to reproduce the bug. A minimal, self-contained code example is highly appreciated.

3.  **Expected vs. Actual Behavior**: Clearly describe what you expected to happen and what actually happened.

**Feature Requests**

If you have an idea for a new feature or an improvement to an existing one, please open an issue to start a discussion. Describe the functionality you'd like to see and your use case.

Contributing Code
-----------------

If you'd like to contribute code by fixing a bug or adding a new feature, please follow this standard workflow:

1.  **Fork the Repository**: Create your own fork of the `Melodie repository <https://github.com/ABM4ALL/Melodie>`_ on GitHub.

2.  **Developer Installation**: Set up your local development environment by following the *Developer Installation* instructions in the :doc:`installation` guide.

3.  **Create a Branch**: Create a new branch from ``main`` for your changes. A descriptive name is helpful (e.g., ``fix-visualizer-bug`` or ``feature-new-network-type``).

4.  **Make Changes**: Implement your bug fix or new feature. Ensure your code follows the existing style and includes appropriate docstrings and comments.

5.  **Run Tests**: Before submitting, please run the test suite to ensure your changes haven't introduced any regressions.

6.  **Submit a Pull Request (PR)**: Push your branch to your fork and open a pull request against the ``main`` branch of the Melodie repository. Provide a clear title and description of your changes.

Adding to the Model Gallery
---------------------------

We are also excited to showcase models developed with Melodie! If you have a project you'd like to share with the community, you can contribute by:

1.  Adding the complete and runnable source code of your model to the ``examples/`` directory.
2.  Creating a corresponding documentation page in the :doc:`gallery/_index` section, explaining the model's concept and implementation.

This is a great way to share your work and help others learn Melodie.
