Framework Comparison
====================

For those familiar with `Mesa <https://github.com/projectmesa/mesa>`_ or `AgentPy
<https://github.com/JoelForamitti/agentpy>`_, this page offers a comparison
between **Melodie** and these two popular frameworks. To provide a concrete
basis for discussion, this repository contains three parallel implementations of
the same simple ``CovidContagion`` model.

Project Structure
-----------------

The three aligned examples live in the ``examples/`` directory:

.. code-block:: text

    examples/
    ├── covid_contagion              (Melodie)
    ├── covid_contagion_mesa         (Mesa)
    └── covid_contagion_agentpy      (AgentPy)

All three models reuse the same ``data/input/SimulatorScenarios.csv`` and
``ID_HealthState.csv`` files. Their outputs (agent and environment/model data)
are written to their respective ``data/output`` folders in a comparable CSV
format, allowing for a direct, side-by-side analysis of both the code and the
results.

High-Level Comparison
---------------------

While all three frameworks can achieve similar outcomes, their design
philosophies and core abstractions differ.

**Architecture & Core Components**

    - **Melodie**: Emphasizes a clear separation of concerns with explicit,
      first-class components: ``Model`` (orchestrator), ``Environment``
      (macro-level logic and interactions), ``Agent`` (micro-level logic),
      ``Scenario`` (inputs), and ``DataCollector`` (outputs). The simulation's
      timeline is clearly defined in the ``Model.run()`` method.
    - **Mesa**: Adopts a more "Model-centric" approach where most logic and state
      (including parameters and macro-variables) reside on the ``Model``
      object. In versions prior to 3.0, it relied heavily on a ``Scheduler``;
      Mesa 3.0+ encourages simpler, explicit agent list management (e.g.,
      manually shuffling and iterating over agents), as shown in our example.
    - **AgentPy**: Also Model-centric, with parameters accessed through the
      ``self.p`` dictionary. It integrates scheduling and agent-set operations
      directly into its powerful ``AgentList`` object, offering concise ways
      to manage agent populations.

**Scenario & Parameter Handling**

    - **Melodie**: The ``Scenario`` object is the single source of truth for all
      inputs. It loads data via its ``load_data()`` method and makes it
      available to all other components as ``self.scenario.xxx``.
    - **Mesa & AgentPy**: Lack a built-in ``Scenario`` concept. Parameters are
      typically passed as a dictionary to the model's constructor. In our
      examples, we manually read the CSV with ``pandas`` to achieve parity.

**Data Collection**

    - **Melodie**: The ``DataCollector`` is an explicit component where you
      register which agent and environment properties to save. It handles the
      database/CSV writing automatically.
    - **Mesa**: Also features an explicit ``DataCollector`` where you register
      "reporters" for model and agent variables.
    - **AgentPy**: Data collection is often more manual. While it offers advanced
      reporters in its ``Experiment`` module, in a basic model run, it is
      common to manually append data to lists and convert them to a
      ``pandas.DataFrame`` at the end, as done in our example.

**Running the Model**

    - **Melodie**: The ``Simulator`` is a high-level manager that automatically
      handles iterating through scenarios and runs defined in the input CSV.
    - **Mesa & AgentPy**: The examples here use a manual loop in ``main.py`` to
      iterate through scenarios and runs to match Melodie's output structure. For
      simpler use cases, one would typically run a single scenario directly.

A Note on This Comparison
-------------------------

To enable an "apples-to-apples" comparison, the Mesa and AgentPy examples in
this repository are intentionally written to be compatible with Melodie's I/O
format (reading ``SimulatorScenarios.csv``, handling multiple runs, and saving
two separate output CSVs). The examples use **Mesa >= 3.0** and **AgentPy >= 0.1.5**.
A more idiomatic, minimal example in Mesa or AgentPy might be simpler, for instance,
by defining parameters directly in the code and using a more basic output format.

Advanced Features in Melodie
----------------------------

Beyond the core simulation loop, Melodie also provides "Modeling Managers" for
more advanced use cases, which are not present in Mesa or AgentPy.

*   ``Simulator``: The standard manager for running simulations.
*   ``Calibrator``: Helps find optimal model parameters by minimizing the
    distance between simulation output and empirical data.
*   ``Trainer``: Trains agents to optimize their individual behaviors using
    evolutionary algorithms.

Detailed examples for the ``Calibrator`` and ``Trainer`` will be provided in the
Model Gallery.
