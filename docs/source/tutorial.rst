
Tutorial
========

This tutorial provides an example modeling the contagion process of Covid-19 virus in a population of agents.
It is a minimum example of Melodie, but also shows a clear project structure and the use of most important modules.

The project structure is shown as below.

::

    CovidContagion
    ├── data
    │   ├── input
    │   │   ├── input
    │   └── output
    ├── source
    │   ├── agent.py
    │   ├── environment.py
    │   ├── data_collector.py
    │   ├── data_info.py
    │   ├── data_loader.py
    │   ├── scenario.py
    │   ├── model.py
    │   └── analyzer.py
    ├── config.py
    ├── run_simulator.py
    ├── run_analyzer.py
    └── readme.md

Agent
_____

agent

.. code-block:: Python

   from Melodie import Simulator

Environment
___________

environment





