CovidContagionGrid
==================

This example extends the base ``covid_contagion`` model by introducing Melodie's **Grid** module.
It demonstrates how to simulate agents moving and interacting in a 2D spatial environment.

Project Structure (Grid)
------------------------

The structure mirrors the base example but includes specific grid-related implementations:

.. code-block:: text

    examples/covid_contagion_grid
    ├── core/
    │   ├── agent.py            # Agents with spatial coordinates (x, y)
    │   ├── grid.py             # Definition of Grid and Spot classes
    │   ├── environment.py      # Orchestrates agent movement and infection
    │   ├── model.py            # Initializes the grid and places agents
    │   ├── scenario.py         # Loads parameters and grid-related matrices
    │   └── ...
    ├── data/
    │   ├── input/
    │   │   ├── SimulatorScenarios.csv      # Adds grid_x_size, grid_y_size
    │   │   ├── ID_HealthState.csv          # Same as base example
    │   │   └── Parameter_GridStayProb.csv  # 2D matrix controlling movement
    │   └── output/
    └── ...

Key Differences from Base Model
-------------------------------

1. **Spatial Agents (`GridAgent`)**:
   Agents now inherit from ``GridAgent`` instead of ``Agent``. This gives them ``x`` and ``y`` attributes and built-in methods for movement.

   * **Category**: The ``set_category()`` method is required for ``GridAgent``. It assigns an integer ID to the agent type (e.g., 0 for humans, 1 for animals). This is used by the Grid to:
   
     - Efficiently manage multiple types of agents on the same map.
     - Return ``(category, id)`` tuples when querying neighbors.
     - Differentiate agents for visualization (e.g., drawing humans as circles and hospitals as crosses).

2. **The Grid and Spots**:
   We define a ``CovidGrid`` and ``CovidSpot``.
   - Each **Spot** represents a cell on the grid and can hold properties (e.g., ``stay_prob``).
   - The **Grid** manages these spots and agent positions.

3. **Movement Logic**:
   Agents decide whether to move based on the ``stay_prob`` of their current spot. If they move, they choose a random neighbor cell.

4. **Spatial Infection**:
   Infection now happens locally. An infected agent searches for neighbors within a certain radius (Moore neighborhood by default) and tries to infect them.

Scenario & Input Data
---------------------

The ``CovidScenario`` class is updated to load spatial data:

- **Grid Dimensions**: Loaded from ``SimulatorScenarios.csv`` (``grid_x_size``, ``grid_y_size``).
- **Spatial Heterogeneity**: A matrix file ``Parameter_GridStayProb.csv`` is loaded to set the ``stay_prob`` for each spot on the grid.

.. code-block:: python

    class CovidScenario(Scenario):
        def load_data(self) -> None:
            self.health_states = self.load_dataframe("ID_HealthState.csv")
            # Load the 2D matrix for spot properties
            self.stay_prob_matrix = self.load_matrix("Parameter_GridStayProb.csv")

Implementation Details
----------------------

Model Setup (`core/model.py`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../../examples/covid_contagion_grid/core/model.py
   :language: python
   :linenos:

Environment Logic (`core/environment.py`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../../examples/covid_contagion_grid/core/environment.py
   :language: python
   :linenos:

Spatial Agent (`core/agent.py`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../../examples/covid_contagion_grid/core/agent.py
   :language: python
   :linenos:

Grid Definition (`core/grid.py`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../../examples/covid_contagion_grid/core/grid.py
   :language: python
   :linenos:

Running the Model
-----------------

Run the model using the provided entry script:

.. code-block:: bash

   python examples/covid_contagion_grid/main.py

This will generate ``Result_Simulator_Agents.csv`` and ``Result_Simulator_Environment.csv`` in the ``data/output`` folder.
