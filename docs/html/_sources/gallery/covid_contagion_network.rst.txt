CovidContagionNetwork
=====================

This example demonstrates how to use Melodie's **Network** module to model contagion spread.
Instead of moving on a grid, agents are connected via edges in a graph (network), and infection transmits through these connections.

Project Structure (Network)
---------------------------

The structure is similar to other examples but includes network-specific configurations:

.. code-block:: text

    examples/covid_contagion_network
    ├── core/
    │   ├── agent.py            # NetworkAgent (inherits from NetworkAgent)
    │   ├── environment.py      # Handles infection propagation through network edges
    │   ├── model.py            # Initializes the network and agent connections
    │   ├── scenario.py         # Defines network topology parameters
    │   └── ...
    ├── data/
    │   ├── input/
    │   │   ├── SimulatorScenarios.csv      # Defines network type and params (k, p, m)
    │   │   └── ID_HealthState.csv
    │   └── output/
    └── ...

Key Differences from Base Model
-------------------------------

1. **Network Agents (`NetworkAgent`)**:
   Agents inherit from ``Melodie.NetworkAgent``. They don't have coordinates but have a ``set_category()`` method to identify their node type in the graph.

2. **The Network**:
   We use ``Melodie.Network`` (built on top of NetworkX) to manage connections.
   
   * **Topology**: The network structure (e.g., Small World, Scale-Free) is determined by scenario parameters.
   * **Neighbors**: Agents interact only with their directly connected neighbors.

3. **Propagation Logic**:
   Instead of spatial distance, infection occurs via edges:
   
   * An infected agent checks its connected neighbors.
   * If a neighbor is susceptible, infection may occur based on ``infection_prob``.

Scenario & Input Data
---------------------

The ``SimulatorScenarios.csv`` controls the network structure for each run.
Supported network types in this example include:

* **Watts-Strogatz (`watts_strogatz_graph`)**: Requires parameters ``k`` (neighbors) and ``p`` (rewiring probability).
* **Barabási-Albert (`barabasi_albert_graph`)**: Requires parameter ``m`` (edges for new nodes).

.. code-block:: csv

    id,network_type,network_param_k,network_param_p,network_param_m,...
    0,watts_strogatz_graph,4,0.1,0,...
    1,barabasi_albert_graph,0,0.0,3,...

Implementation Details
----------------------

Model Setup (`core/model.py`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The model creates the network and sets up connections using ``setup_agent_connections``.

.. literalinclude:: ../../../examples/covid_contagion_network/core/model.py
   :language: python
   :linenos:

Environment Logic (`core/environment.py`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The environment iterates through infected agents and accesses their neighbors via ``self.model.network.get_neighbors()``.

.. literalinclude:: ../../../examples/covid_contagion_network/core/environment.py
   :language: python
   :linenos:

Network Agent (`core/agent.py`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Agents are simple state-machines but must implement ``set_category()``.

.. literalinclude:: ../../../examples/covid_contagion_network/core/agent.py
   :language: python
   :linenos:

Scenario Configuration (`core/scenario.py`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The scenario class parses the CSV parameters into a dictionary format that NetworkX expects.

.. literalinclude:: ../../../examples/covid_contagion_network/core/scenario.py
   :language: python
   :linenos:

Data Collector (`core/data_collector.py`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Collects both macro-level environment statistics (S-I-R counts) and micro-level agent states.

.. literalinclude:: ../../../examples/covid_contagion_network/core/data_collector.py
   :language: python
   :linenos:

Running the Model
-----------------

Run the model using the entry script:

.. code-block:: bash

   python examples/covid_contagion_network/main.py

Results (e.g., ``CovidContagionNetwork_Simulator_Environment.csv``) will show the S-I-R curves, which may differ significantly depending on the network topology.
