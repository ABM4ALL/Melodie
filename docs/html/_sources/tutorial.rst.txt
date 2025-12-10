Tutorial
========

This tutorial uses the **covid_contagion** minimal example to demonstrate the Melodie
architecture. The code is kept simple but covers all core components. The project
structure is as follows:

::

    examples/covid_contagion
    ├── core
    │   ├── agent.py
    │   ├── environment.py
    │   ├── model.py
    │   ├── scenario.py
    │   └── data_collector.py
    ├── data
    │   ├── input
    │   │   ├── SimulatorScenarios.csv
    │   │   └── ID_HealthState.csv
    │   └── output
    │       ├── Result_Simulator_Agents.csv
    │       └── Result_Simulator_Environment.csv
    ├── main.py
    └── README.md

Conceptually, Melodie encourages **separation of concerns** in an ABM. In this example, the main components are:

- *Model* (``core/model.py``) wires all components together and defines the main time loop.
- *Scenario* (``core/scenario.py``) is the single entry point for all model inputs. It loads all data from ``data/input`` (including ``SimulatorScenarios``), and other components access this data via ``self.scenario.xxx``.
- *Environment* (``core/environment.py``) implements the model's macro-level logic. It coordinates agent interactions and calculates population-level statistics.
- *Agents* (``core/agent.py``) implement the model's micro-level logic. They only know their own state and how to update it based on scenario parameters or environment instructions.
- *DataCollector* (``core/data_collector.py``) specifies what data to record from agents and the environment, and saves it to ``data/output``.

The **covid_contagion** example is deliberately simple to make this architecture clear. It contains one type of agent, one environment, one model, and one scenario table.

Model
-----

The Model creates components, drives the simulation steps, and collects outputs. It orchestrates the simulation but does **not** contain domain-specific logic itself—that belongs in the Agent and Environment classes.

.. literalinclude:: ../../examples/covid_contagion/core/model.py
   :language: python
   :linenos:

Notes:

- ``create``: Builds the AgentList, Environment, and DataCollector.
- ``setup``: Initializes agents and sets up the initial infection.
- ``run``: Executes the main simulation loop, calling the environment for agent interaction and recovery, and then saving the results.

Think of the Model as the **orchestrator of components**: it decides *what components exist*, in *what order* they are called each period, and delegates the concrete simulation logic to them. This allows you to reuse Agent and Environment classes in different experimental setups by only changing the ``run`` logic in the Model.

Scenario Definition
-------------------

The Scenario defines parameters and loads static data tables. It acts as the single source of truth for all configuration and input data, allowing the other components to focus on behavior rather than I/O.

.. literalinclude:: ../../examples/covid_contagion/core/scenario.py
   :language: python
   :linenos:

Some column names in ``SimulatorScenarios`` have a special meaning in Melodie:

- ``id``: A unique identifier for the scenario, used in output files.
- ``run_num``: How many times to repeat the same scenario. This is useful for analyzing stochastic models to observe the variability of outcomes. Defaults to ``1`` if omitted.
- ``period_num``: How many periods the model will run. Defaults to ``0`` if omitted (the simulation loop will not execute).

These special attributes are defined in the base ``Melodie.Scenario`` class. They are typically controlled by adding corresponding columns to ``SimulatorScenarios``, but you do not need to redeclare them in your subclass's ``setup`` method unless you want explicit type hints. Other columns are user-defined.

The ``load_data`` method is a special hook that is automatically called by Melodie, so you should not change its name. It runs after parameters are loaded from the current ``SimulatorScenarios`` row. Inside ``load_data``, you can load any other required data tables and attach them as attributes to the scenario instance. All other components (Model, Agent, Environment) can then access this data uniformly via ``self.scenario.xxx``. For data-heavy models, you can also pre-process large tables in ``load_data`` (e.g., into dictionaries) to improve performance.

Environment Logic
-----------------

The Environment coordinates interactions, the initial infection, and recovery. It acts as the "director" that arranges agent interactions and maintains macro-level summaries.

.. literalinclude:: ../../examples/covid_contagion/core/environment.py
   :language: python
   :linenos:

Notes:

- ``setup_infection``: Sets the initial number of infected agents via a Bernoulli trial for each susceptible agent.
- ``agents_interaction``: A simple mean-field interaction where each infected agent randomly meets one other agent and may spread the virus.
- ``agents_recover``: Delegates the recovery logic to each agent.
- ``update_population_stats``: Aggregates micro-level agent states into macro-level population counts.

Agent Behavior
--------------

The Agent defines micro-level state and behavior. Agents in Melodie are deliberately lightweight: they only store their own state and expose methods for state transitions. The Environment decides *when* these methods are called.

.. literalinclude:: ../../examples/covid_contagion/core/agent.py
   :language: python
   :linenos:

Notes:

- State: ``health_state`` (0: susceptible, 1: infected, 2: recovered).
- Method: ``health_state_update`` contains the logic for an agent to recover from infection.

This "smart environment, simple agents" pattern is a core design principle in Melodie. It keeps agent classes simple and testable, centralizes interaction logic in the Environment, and makes it easier to modify interaction rules (e.g., from random-mixing to a grid-based model) without changing agent code.

Data Collection Setup
---------------------

The Data Collector specifies which micro and macro results to save to ``data/output``.

.. literalinclude:: ../../examples/covid_contagion/core/data_collector.py
   :language: python
   :linenos:

The key design idea is that **data collection is explicit**: you register exactly which properties to track, and Melodie handles the indexing by scenario, run, period, and agent ID in a consistent format. This separates the simulation logic from the data storage logic.

Run the model
-------------

To run the example from the repository root (after activating your virtual environment):

.. code-block:: bash

   python examples/covid_contagion/main.py

This ``main.py`` file is the entry point that loads the configuration and starts the simulation. It mirrors how you would run any Melodie project from a script.

.. literalinclude:: ../../examples/covid_contagion/main.py
   :language: python
   :linenos:

Notes:

- It is recommended to use absolute paths for input/output folders to avoid ambiguity.
- The ``Simulator`` automatically finds the scenario table by its name, ``SimulatorScenarios`` (both ``.csv`` and ``.xlsx`` are supported).
- The *Config* object tells Melodie **where** data lives on disk.
- The *Simulator* object knows **how** to iterate over scenarios and runs.

When you start a simulation, the ``Simulator`` automatically calls a set of lifecycle methods on your components in a fixed order:

- On each ``Scenario``: ``setup()``, then ``load_data()``, then ``setup_data()`` (if implemented).
- On the ``Model``: ``create()``, then ``setup()``, then ``run()``.
- On components like Environment, AgentList, and DataCollector: their respective ``setup()`` methods.

This is why these method names are a fixed convention. You rarely call these methods directly—the ``Simulator`` manages the full execution loop for you.

After a run, the ``data/output`` folder will contain CSV files for analysis:

- ``Result_Simulator_Agents.csv``: Per-period agent states.
- ``Result_Simulator_Environment.csv``: Per-period environment aggregates (the macro metrics registered in the DataCollector).
