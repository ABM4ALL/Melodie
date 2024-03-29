
CovidGridContagion
==================

To show how the ``Melodie.Grid`` module can be used,
we provide this `CovidGridContagion <https://github.com/ABM4ALL/CovidGridContagion>`_ model,
which is based the `CovidContagion <https://github.com/ABM4ALL/CovidContagion>`_ model.
So, if you haven't, we will strongly suggest to read the :ref:`Tutorial` section first.

The differences are:

* Agents walk on a 2D ``grid`` randomly.
* The ``grid`` is constructed with spots. Each ``spot`` has an attribute ``stay_prob``, which decides if the agent standing on this spot will move probabilistically.
* The infected agents can pass the virus to the other uninfected agents in the neighborhood.

Project Structure
_________________

The project structure is as below.
Compared with the structure of the `CovidContagion <https://github.com/ABM4ALL/CovidContagion>`_ model,
one ``grid.py`` file is added in the ``source`` folder,
and one ``Parameter_GridStayProb.xlsx`` file is added in the ``data/input`` folder.

::

    CovidGridContagion
    ├── data
    │   ├── input
    │   │   ├── SimulatorScenarios.xlsx
    │   │   ├── ID_HealthState.xlsx
    │   │   ├── ID_AgeGroup.xlsx
    │   │   ├── Parameter_GridStayProb.xlsx
    │   │   └── Parameter_AgeGroup_TransitionProb.xlsx
    │   └── output
    │       ├── CovidGridContagion.sqlite
    │       ├── PopulationInfection_S0R0.png
    │       └── PopulationInfection_S1R0.png
    ├── source
    │   ├── agent.py
    │   ├── environment.py
    │   ├── grid.py
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

Grid and Spot
_____________

To include such differences about ``grid``, ``Melodie`` provides two classes ``Grid`` and ``Spot``,
based on which the ``CovidGrid`` and ``CovidSpot`` classes are defined.

.. code-block:: Python
   :caption: grid.py
   :linenos:
   :emphasize-lines: 15

   from Melodie import Spot, Grid
   from source import data_info


   class CovidSpot(Spot):

       def setup(self):
           self.stay_prob = 0.0


   class CovidGrid(Grid):

       def setup(self):
           self.set_spot_property(
               "stay_prob", self.scenario.get_matrix(data_info.grid_stay_prob)
           )

As shown, the two classes are defined in brief, i.e., most functions and attributes are inherited from ``Melodie``.
The only reason to define this ``CovidGrid`` class for the model, is to include the ``stay_prob`` attribute of each ``CovidSpot``.
Or, one can also use the ``Grid`` and ``Spot`` classes of ``Melodie`` directly.

Matrix Data
___________

The ``stay_prob`` values of the spots are saved in a matrix, which is the same size with the grid.
Like other dataframes, the matrix is first registered in the ``data_info.py`` and loaded by the ``data_loader``,
then can be accessed by the ``scenario`` object by using ``get_matrix`` function (Line 15).
The registry of the matrix is as follows.

.. code-block:: Python
   :caption: data_info.py
   :linenos:

   import sqlalchemy

   from Melodie import MatrixInfo


   grid_stay_prob = MatrixInfo(
       mat_name="grid_stay_prob",
       data_type=sqlalchemy.Float(),
       file_name="Parameter_GridStayProb.xlsx",
   )

Model
_____

With the classes and data, the next step is to include the ``grid`` object as a new component of the ``model``.
As shown in Line 24, ``Melodie.Model`` provides a ``create_grid`` function,
taking the two class variables as input - ``CovidGrid`` and ``CovidSpot``.

.. code-block:: Python
   :caption: model.py
   :linenos:
   :emphasize-lines: 24, 31-35

   from typing import TYPE_CHECKING

   from Melodie import Model

   from source import data_info
   from source.agent import CovidAgent
   from source.data_collector import CovidDataCollector
   from source.environment import CovidEnvironment
   from source.grid import CovidGrid
   from source.grid import CovidSpot
   from source.scenario import CovidScenario

   if TYPE_CHECKING:
       from Melodie import AgentList


   class CovidModel(Model):
       scenario: "CovidScenario"

       def create(self):
           self.agents: "AgentList[CovidAgent]" = self.create_agent_list(CovidAgent)
           self.environment = self.create_environment(CovidEnvironment)
           self.data_collector = self.create_data_collector(CovidDataCollector)
           self.grid = self.create_grid(CovidGrid, CovidSpot)

       def setup(self):
           self.agents.setup_agents(
               agents_num=self.scenario.agent_num,
               params_df=self.scenario.get_dataframe(data_info.agent_params),
           )
           self.grid.setup_params(
               width=self.scenario.grid_x_size,
               height=self.scenario.grid_y_size
           )
           self.grid.setup_agent_locations(self.agents)

In the ``setup`` function, the ``grid`` needs to be initialized with size parameters from ``scenario``.
Then, the agents need to be located on the ``grid``,
which requires that they are already initialized with the attributes ``x`` and ``y``.

GridAgent
_________

The agents that can walk on the grid are defined by inheriting the ``GridAgent`` class of ``Melodie``.
They have three additional attributes: ``category``, ``x``, and ``y``.
Additionally, they also have access to the ``grid`` (Line 26) and some grid-related functions,
e.g., ``rand_move_agent`` in Line 32.

.. code-block:: Python
   :caption: agent.py
   :linenos:
   :emphasize-lines: 18, 22-23, 28, 32, 35-36

   import random
   from typing import TYPE_CHECKING

   from Melodie import GridAgent

   if TYPE_CHECKING:
       from source.scenario import CovidScenario
       from Melodie import AgentList
       from source.grid import CovidSpot
       from source.grid import CovidGrid


   class CovidAgent(GridAgent):
       scenario: "CovidScenario"
       grid: "CovidGrid[CovidSpot]"
       spot: "CovidSpot"

       def set_category(self):
           self.category = 0

       def setup(self):
           self.x: int = 0
           self.y: int = 0
           self.health_state: int = 0
           self.age_group: int = 0

       def move(self):
           spot: "CovidSpot" = self.grid.get_spot(self.x, self.y)
           stay_prob = spot.stay_prob
           if random.uniform(0, 1) > stay_prob:
               move_radius = 1
               self.rand_move_agent(move_radius, move_radius)

       def infection(self, agents: "AgentList[CovidAgent]"):
           neighbors = self.grid.get_neighbors(self)
           for neighbor_category, neighbor_id in neighbors:
               neighbor_agent: "CovidAgent" = agents.get_agent(neighbor_id)
               if neighbor_agent.health_state == 1:
                   if random.uniform(0, 1) < self.scenario.infection_prob:
                       self.health_state = 1
                       break

One thing that might be confused: Why is there the ``category`` attribute?

The ``category`` attribute is to make sure that, when there are multiple groups of agents walking on the ``grid``,
the ``grid`` can distinguish them and work well.
So, the function ``set_category`` much be implemented in a class that inherits the ``GridAgent`` class.
For example, as shown in Line 35-36, when iterating through the ``neighbors`` returned by ``grid.get_neighbors``,
each neighbor is indexed with both ``category`` and the ``id`` of the agent.

For more details of the ``Grid`` and ``Spot`` modules,
please refer to the :ref:`API Reference` section.






















