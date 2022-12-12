
Introduction
============

Agent-based Model (ABM)
-----------------------

ABMs characterize physical, biological, and social economic systems as dynamic `interactions` among `agents` from a bottom-up perspective.
The `agents` can be molecules, animals, or human beings.
The `interactions` can be water molecules forming a vortex, ants searching for food, or people trading stocks in the market.

Agents' interactions can bring `emergent properties` to a system and turn it into a `complex system`.
To model such mechanism is usually the core reason for using ABMs.
Besides, taking social economic systems as example, ABMs are also flexible to consider agents'
(1) `heterogeneity` (e.g., wealth, risk attitude, preference, decision-making rule, etc.) based on micro-data;
(2) `bounded rationality and adaptation behavior` based on psychological and behavioral studies.

Melodie Framework
-----------------

As a general framework for developing agent-based models (ABMs),
**Melodie** is designed in a modular structure and the modules are organized into four clusters:
**Model**, **Scenario**, **Modeling Manager**, and **Infrastructure**.

Model
~~~~~

The modules in the **Model Cluster** focus on describing the logics of the target system.
Developed with ``Melodie``, a ``model: Model`` object can contain following components:

* ``agent: Agent`` - makes decisions, interacts with others, and stores the micro-level variables.
* ``agents: AgentList`` - contains a list of agents and provides relevant functions.
* ``environment: Environment`` - coordinates the agents' decision-making and interaction processes and stores the macro-level variables.
* ``data_collector: DataCollector`` - collects the micro- and macro-level variables from the agents and environment, then saves them to the database.
* ``grid: Grid`` - constructed with ``spot: Spot`` objects, describes the grid (*if exists*) that the agents walk on, stores grid variables, and provides the relevant functions.
* ``network: Network`` - constructed with ``edge: Edge`` objects, describes the network (*if exists*) that links the agents, and provides the relevant functions.

Scenario
~~~~~~~~

The modules in the **Scenario Cluster** focus on formatting, importing,
and delivering the input data to the ``model``. The modules include

* ``DataFrameInfo`` and ``MatrixInfo`` - provide standard format for input tables as parameters.
* ``DataLoader`` - whose object loads all the input data into the ``model``.
* ``Scenario`` - whose object contains all the input data that is needed to run the model, and can be accessed by the ``model``, the ``environment``, the ``data_collector``, and each ``agent``.

Modelling Manager
~~~~~~~~~~~~~~~~~

To combine everything and finally start running, the **Modelling Manager Cluster** includes three modules in parallel,
which can be constructed and run for different objectives:

* ``Simulator`` - simulates the logics written in the ``model``.
* ``Calibrator`` - calibrates the parameters of the ``scenario`` by minimizing the distance between model output and empirical evidence.
* ``Trainer`` - trains the ``agents`` to update their behavioral parameters for higher payoff.

Taking the CovidContagion model in the tutorial as example, as shown below,
the ``simulator`` is initialized with a ``config`` object (incl. project name and folder paths) and
the class variables of the ``model``, the ``scenario``, and the ``data_loader``.

.. code-block:: Python

   from Melodie import Simulator
   from config import config
   from source.model import CovidModel
   from source.scenario import CovidScenario
   from source.data_loader import CovidDataLoader

   simulator = Simulator(
        config=config,
        model_cls=CovidModel,
        scenario_cls=CovidScenario,
        data_loader_cls=CovidDataLoader
   )
   simulator.run()

At last, by calling the ``simulator.run`` function, the simulation starts.

.. comment::

    Studio
    ~~~~~~

    Optional modules for visualization, incl. interactive figures and database.
    Or, shall we make it open-source at all? The three clusters above are already well enough for research.

    We can plan a few separate modules surrounding **Melodie** for developing products like AMETS for business.

    * MelodieStudio
    * MelodieData - RenderDict, DataFrameInfo, etc.

    The **Studio Cluster** includes the modules

    * ``Visualizer`` -
    * ``MelodieStudio`` -

Infrastructure
~~~~~~~~~~~~~~

The last **Infrastructure Cluster** includes the modules that provide support for the modules above.

* ``Config`` - provides the channel to define project information, e.g., project name, folder paths.
* ``DBConn`` - provides the functions to write to or read from the database.
* ``MelodieException`` - provides the pre-defined exceptions in Melodie to support debugging.









