
Introduction
============

Agent-based Model (ABM)
_______________________

ABMs characterize physical, biological, and social economic systems as dynamic `interactions` among `agents` from a bottom-up perspective.
The `agents` can be molecules, animals, or human beings.
The `interactions` can be water molecules forming a vortex, ants searching for food, or people trading stocks in the market.

Agents' interactions can bring `emergent properties` to a system and turn it into a `complex system`.
To model such mechanism is usually the core reason for using ABMs.
Besides, taking social economic systems as example, ABMs are also flexible to consider agents'
(1) `heterogeneity` (e.g., wealth, risk attitude, preference, decision-making rule, etc.) based on micro-data;
(2) `bounded rationality and adaptation behavior` based on psychological and behavioral studies.

Melodie Framework
_________________

As a general framework for developing agent-based models (ABMs),
**Melodie** is designed in a modular structure and the modules are organized into four clusters:
**Model**, **Scenario**, **Modeling Manager**, and **Infrastructure**.

The Model
~~~~~~~~~

The modules in the **Model Cluster** focus on describing the logics of the target system.
Developed with **Melodie**, a ``model: Model`` object can contain following components:

* ``agent: Agent`` - makes decisions, interacts with others, and stores the micro-level variables.
* ``agents: AgentList`` - contains a list of agents and provides relevant functions.
* ``environment: Environment`` - coordinates the agents' decision-making and interaction processes and stores the macro-level variables.
* ``data_collector: DataCollector`` - collects the micro- and macro-level variables from the agents and environment, then saves them to the database.
* ``grid: Grid`` - constructed with ``spot: Spot`` objects, describes the grid (*if exists*) that the agents walk on, stores grid variables, and provides the relevant functions.
* ``network: Network`` - constructed with ``edge: Edge`` objects, describes the network (*if exists*) that links the agents, and provides the relevant functions.

The Scenario
~~~~~~~~~~~~

The modules in the **Scenario Cluster** focus on formatting, importing,
and delivering the input data to the ``model``. 

* ``Scenario`` - is the central component for data handling. Its instance contains all input data needed to run the model. It can load data directly via its ``load_data`` method, making it accessible to all other model components.
 
Modelling Manager
~~~~~~~~~~~~~~~~~

To combine everything and finally start running, the **Modelling Manager Cluster** includes three modules in parallel,
which can be constructed and run for different objectives:

* ``Simulator`` - simulates the logics written in the ``model``.
* ``Calibrator`` - calibrates model parameters by minimizing the distance between simulation output and empirical data.
* ``Trainer`` - trains agents to find behavioral parameters that optimize their payoffs.
 
Taking the ``CovidContagion`` model from the tutorial as an example, the ``Simulator`` is initialized with a ``Config`` object and the classes for the ``Model`` and ``Scenario``.
 
.. code-block:: python
 
   import os
   from Melodie import Config, Simulator
   from core.model import CovidModel
   from core.scenario import CovidScenario

   # In a real script, 'core' would be the folder containing your model files.
   
   config = Config(
       project_name="CovidContagion",
       project_root=os.path.dirname(__file__),
       input_folder="data/input",
       output_folder="data/output",
   )
 
    simulator = Simulator(
         config=config,
         model_cls=CovidModel,
         scenario_cls=CovidScenario
    )
    simulator.run()
 
At last, by calling the ``simulator.run()`` method, the simulation starts.

Infrastructure
~~~~~~~~~~~~~~

The **Infrastructure Cluster** provides a rich set of foundational modules that support the entire framework. Key components include:

* ``Config``: A centralized object for managing all project settings, such as names and file paths.
* ``DBConn``: Handles database connections, allowing models to read from and write to databases.
* ``Parallel``: Provides the backend for parallel simulation runs.
* ``Visualizer`` & ``MelodieStudio``: An API (``Visualizer``) to connect the simulation to ``MelodieStudio`` (a separate package) for real-time, browser-based visualization.
* ``Table`` & ``JSONObject``: Utilities for robust data handling, serialization, and validation.
* ``MelodieException``: A set of pre-defined custom exceptions to aid in debugging and error handling.



















