
Introduction
============

This document gives a brief introduction of agent-based models and an overview of the main modules in the Melodie library.
For further details, please read the tutorial and API reference.

Agent-based models
------------------

Agent-based models (ABMs) characterize physical, biological, and social economic systems as dynamic `interactions`
among `agents` from a bottom-up perspective. The `agents` can be molecules, animals, or human beings. The `interactions`
can be water molecules forming a vortex, ants searching for their food, or people trading stocks in the market.

Agents' interactions can bring emergent properties to a system and turn it into a complex system.
This is the first reason why we use an ABM to model a target system.
Furthermore, for the social economic systems, ABMs can model agents'
(1) attribute and behavior heterogeneity, based on micro-level empirical evidence; and
(2) bounded rationality and adaptation behavior, based on psychological and behavioral studies.
These advantages support agent-based modeling to be an alternative paradigm for the neo-classical economics.

Melodie
-------

As a general framework for developing ABMs, **Melodie** has three groups of modules:

* `Block`:  ``model``, ``scenario``, ``dataframe_loader``, ``environment``, ``agent_list``, ``data_collector``, ``grid``, ``network``.
* `Operator`: ``simulator``, ``calibrator``, ``trainer``.
* `Infrastructure`: ``db``, ``studio``.

.. format a bit and link to the api reference pages

Block modules
^^^^^^^^^^^^^

The `Block` modules are used to construct an ABM, and six of them are always necessary.

* ``model`` is the container of the following components.
* ``scenario`` contains the input data.
* ``dataframe_loader`` loads the input data to ``scenario``.
* ``agent_list`` contains the ``agents`` and one model can have several ``agent_list``.
* ``environment`` contains the macro-level parameters and variables and controls the interaction and decision-making of agents.
* ``data_collector`` collects the parameters and variables of the environment and the agents and saves them to the database.

According to the target system, ``model`` could also contain ``grid`` and ``network``.

* ``grid`` is consisted of ``spots`` and represents the geographic surface in the system.
  For example, if the ABM models a city, then ``grid`` can represent the land in the city,
  which consists of 100 ``spots`` (pieces of land). Each ``spot`` can have its own attributes, e.g. available resources.
* ``network`` is consisted of ``edges`` and represents the connection among the ``agents``.
  For example, if the ABM models the information diffusion in a social network, then ``network`` can represent how
  the ``agents`` are connected. Besides, an ``edge`` can also have its own attributes,
  e.g. direction, communication frequency, etc.
* ``visualizer``

Operator modules
^^^^^^^^^^^^^^^^

With **Melodie**, an ABM can be run in different modes by using different `Operator` modules.

* ``simulator`` runs the model simply following the flow written in ``model``.
* ``calibrator`` runs the model iteratively to find the values for a set of parameters by minimizing the
  `distance` between the `model output` and a `target value`.
* ``trainer`` runs the model iteratively to train the `agents` to find smarter `behavioral parameters`.

Infrastructure modules
^^^^^^^^^^^^^^^^^^^^^^

`Infrastructure` modules provide supports the work of other modules or are used for results analysis.

* ``db`` provides the functions for managing the .sqlite database.
* ``studio`` provides the interface to view data from the .sqlite database and displays the plot while running models.


