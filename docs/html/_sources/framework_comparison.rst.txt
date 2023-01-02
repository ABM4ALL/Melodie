
Framework Comparison
====================

For those who work with
`Mesa <https://github.com/projectmesa/mesa>`_ or
`AgentPy <https://github.com/JoelForamitti/agentpy>`_,
we also provide a comparison between **Melodie** and the two packages.
For details, you can find the same CovidContagion model developed with the three packages
in this `repository <https://github.com/ABM4ALL/ABMFrameworkComparison>`_.

Due to our limited experience with **Mesa** and **AgentPy**,
your comments and suggestions are most welcomed if we misunderstand or misuse the two packages.

So, here is a quick summary of the differences:

* First, **Melodie** separates an ``environment`` component from the ``model`` in **Mesa** and **AgentPy**. The ``environment`` has two tasks: (1) it stores the macro-level variables; (2) it coordinates the agents' decision-making and interaction processes. Besides, the ``data_collector`` component is also enhanced with higher configurability.
* Second, **Melodie** provides two dedicated modules for scenario management. The ``data_loader`` loads all input dataframes or matrices into the ``scenario`` object, then the ``scenario`` object is accessed by the ``model`` and its components. Besides, **Melodie** provides the ``DataFrameInfo`` and ``MatrixInfo`` classes to smooth the data processing by the ``data_loader`` and the ``scenario``.
* Third, **Melodie** provides three "modeling managers": ``Simulator``, ``Calibrator``, and ``Trainer``. The latter two can improve the validity of an ABM by (1) calibrating the scenario parameters so that the ``distance`` between the model output and empirical data is minimized; or (2) the agents are trained to update their behavioral parameters for higher payoff.

For further details, please read the sections below.

Project Structure
_________________

The structure of the project in the framework comparison
`repository <https://github.com/ABM4ALL/ABMFrameworkComparison>`_ is shown below.

::

    ABMFrameworkComparison
    ├── data
    │   ├── input
    │   │   ├── SimulatorScenarios.xlsx
    │   │   ├── ID_HealthState.xlsx
    │   │   ├── ID_AgeGroup.xlsx
    │   │   └── Parameter_AgeGroup_TransitionProb.xlsx
    │   └── output
    │       ├── Melodie_CovidContagion.sqlite
    │       ├── Melodie_PopulationInfection_S0R0.png
    │       ├── Melodie_PopulationInfection_S1R0.png
    │       ├── Mesa_PopulationInfection_S0.png
    │       ├── Mesa_PopulationInfection_S1.png
    │       ├── AgentPy_PopulationInfection_S0.png
    │       └── AgentPy_PopulationInfection_S1.png
    ├── source_melodie
    │   ├── agent.py
    │   ├── environment.py
    │   ├── data_collector.py
    │   ├── data_info.py
    │   ├── data_loader.py
    │   ├── scenario.py
    │   ├── model.py
    │   └── analyzer.py
    ├── source_mesa
    │   ├── agent.py
    │   ├── model.py
    │   └── analyzer.py
    ├── source_agentpy
    │   ├── agent.py
    │   ├── model.py
    │   └── analyzer.py
    ├── run_melodie.py
    ├── run_mesa.py
    ├── run_agentpy.py
    └── readme.md

By running ``run_melodie.py``, ``run_mesa.py``, and ``run_agentpy.py``,
you can run the models developed with the three packages with same data in the ``input`` folder.
Then, the result files will all be saved in the ``output`` folder.
For clearer comparison, we try to create the files for different frameworks in a similar structure.
There are more files in the ``source_melodie`` folder and they are explained below.

Model Components
________________

In **Melodie**, the ``model`` is mainly a container of several components and the functions to create and set them up.
The components include ``agents`` (container of ``agent``), ``environment``, ``data_collector``.
Optionally, the ``model`` can also include ``grid`` and ``network``.
Finally, the ``model`` and its components have the ``scenario`` object, which contains all the input data.

However, ``model`` has a mixed role in **Mesa** and **AgentPy**.
The biggest difference between **Melodie** and the two packages is that,
**Melodie** separates the ``environment`` as a new component from the ``model`` in **Mesa** and **AgentPy**.

Melodie
~~~~~~~

As shown in the figure below (`Yu, 2020 <https://ieeexplore.ieee.org/document/9857838/>`_),
``environment`` refers to the "outside" of an individual agent.
**Melodie** follows such conceptualization from the reinforcement learning tradition and
modifies it according to the agent-based modeling context.

.. image:: image/agent_environment.png
   :width: 550
   :align: center

In **Melodie**, the ``environment`` component has two tasks:

* First, it stores the macro-level variables (Line 8-11);
* Second, it coordinates the agents' decision-making and interaction processes (Line 14-16).

.. code-block:: Python
   :caption: environment.py
   :linenos:
   :emphasize-lines: 8-11, 14-16

   from Melodie import Environment
   from Melodie import AgentList
   from source_melodie.agent import CovidAgent

   class CovidEnvironment(Environment):

       def setup(self):
           self.s0 = 0
           self.s1 = 0
           self.s2 = 0
           self.s3 = 0

       @staticmethod
       def agents_health_state_transition(agents: "AgentList[CovidAgent]"):
           for agent in agents:
               agent.health_state_transition()

Then, in the ``model``, there is a ``run`` function where the user can write down the "timeline" of the model, i.e. the steps in each period.
In **Melodie**, these steps are either "``environment`` coordinating agents' decision-making and interaction processes (Line 13-15)" or
"``data_collector`` collecting or saving data (Line 16-17)".

.. code-block:: Python
   :caption: source_melodie/model.py
   :linenos:
   :emphasize-lines: 13-17

   from Melodie import Model
   from source_melodie.scenario import CovidScenario

   if TYPE_CHECKING:
       from Melodie import AgentList


   class CovidModel(Model):
       scenario: "CovidScenario"

       def run(self):
           for period in range(0, self.scenario.period_num):
               self.environment.agents_infection(self.agents)
               self.environment.agents_health_state_transition(self.agents)
               self.environment.calc_population_infection_state(self.agents)
               self.data_collector.collect(period)
           self.data_collector.save()

Finally, **Melodie** runs the model by calling this ``model.run`` function.

Mesa
~~~~

In **Mesa**, the two tasks of the ``environment`` in **Melodie** are done by ``model``:

* First, all the scenario parameters (Line 11-14) and the macro-level variables (Line 15-18) are the attributes of the model.
* Second, regarding "coordinating the agents' decision-making and interaction processes", **Mesa** uses the ``Scheduler`` module (Line 19) and the ``step`` functions defined in the ``Model`` (Line 25), ``Scheduler`` (Line 3 in ``mesa.time.py``) and ``Agent`` (Line 12 in ``source_mesa/agent.py``) classes.

.. code-block:: Python
   :caption: source_mesa/model.py
   :linenos:
   :emphasize-lines: 11-19, 25-26

   import mesa
   import numpy as np
   import pandas as pd

   from source_mesa.agent import CovidAgent


   class CovidModel(mesa.Model):

       def __init__(self, **kwargs):
           self.agent_num = kwargs["agent_num"]
           self.initial_infected_percentage = kwargs["initial_infected_percentage"]
           self.young_percentage = kwargs["young_percentage"]
           self.infection_prob = kwargs["infection_prob"]
           self.s0 = 0
           self.s1 = 0
           self.s2 = 0
           self.s3 = 0
           self.schedule = mesa.time.SimultaneousActivation(self)
           self.datacollector = mesa.DataCollector(
               model_reporters={"s0": "s0", "s1": "s1", "s2": "s2", "s3": "s3"},
               agent_reporters={"health_state": "health_state"}
           )

       def step(self) -> None:
           self.schedule.step()
           self.calc_population_infection_state()
           self.datacollector.collect(self)

.. code-block:: Python
   :caption: mesa.time.py
   :linenos:
   :emphasize-lines: 3, 5

   class SimultaneousActivation(BaseScheduler):

       def step(self) -> None:
           for agent in self._agents.values():
               agent.step()
           for agent in self._agents.values():
               agent.advance()
           self.steps += 1
           self.time += 1

.. code-block:: Python
   :caption: source_mesa/agent.py
   :linenos:
   :emphasize-lines: 12

   import random
   import mesa


   class CovidAgent(mesa.Agent):

       def infection(self, infection_prob: float):
           if self.health_state == 0:
               if random.uniform(0, 1) <= infection_prob:
                   self.health_state = 1

       def step(self) -> None:
           self.infection((self.model.s1 / self.model.num_agents) * self.model.infection_prob)

In **Mesa**, the users must inherit and use all the ``step`` functions that are distributed in different places.
Then, as a result, the representation of the "model timeline" is a major difference between **Melodie** and **Mesa**.

AgentPy
~~~~~~~

In **AgentPy**, like in **Mesa**, the two tasks of the ``environment`` in **Melodie** are done by ``model``:

* First, all the scenario parameters (Line 9-13) and the macro-level variables (Line 14-17) are the attributes of the model.
* Second, to "coordinate the agents' decision-making and interaction processes", **AgentPy** doesn't have the ``Scheduler`` module, but it is integrated into the ``AgentList`` class (Line 8). Taking the ``infection`` function as example (Line 20), it is actually defined in the ``CovidAgent`` class (Line 7 in ``source_agentpy/agent``), but is by default bundled to the ``agents`` and can be called.
.. code-block:: Python
   :caption: source_agentpy/model.py
   :linenos:
   :emphasize-lines: 8-17, 20-21

   import agentpy as ap
   from source_agentpy.agent import CovidAgent


   class CovidModel(ap.Model):

       def setup(self):
           self.agents = ap.AgentList(self, self.p['agent_num'], cls=CovidAgent)
           self.steps = self.p['period_num']
           self.num_agents = self.p["agent_num"]
           self.initial_infected_percentage = self.p["initial_infected_percentage"]
           self.young_percentage = self.p["young_percentage"]
           self.infection_prob = self.p["infection_prob"]
           self.s0 = 0
           self.s1 = 0
           self.s2 = 0
           self.s3 = 0

       def step(self):
           self.agents.infection((self.s1 / self.num_agents) * self.infection_prob)
           self.agents.health_state_transition()
           self.calc_population_infection_state()
           self.record(['s0', 's1', 's2', 's3'])

.. code-block:: Python
   :caption: source_agentpy/agent.py
   :linenos:
   :emphasize-lines: 7

   import random
   import agentpy as ap


   class CovidAgent(ap.Agent):

       def infection(self, infection_prob: float):
           if self.health_state == 0:
               if random.uniform(0, 1) <= infection_prob:
                   self.health_state = 1

Finally, a ``step`` function is defined in the ``model`` (Line 19) and it is called automatically when running the model.
The total ``steps`` of simulation is an attribute of the model and used internally.

Summary
~~~~~~~

In **Melodie**, a new component ``environment`` is separated from the ``model`` in **Mesa** and **AgentPy**
and is dedicated to (1) storing the macro-level variables;
and (2) coordinating the decision-making and interaction processes of agents.

As a result, the model "timeline" can be summarized in the ``model.run`` function.
There is no concept of ``step`` in **Melodie**.
When interacting with the front-end for results visualization,
**Melodie** can still support "step run" with a ``iterator`` tool in the ``model``.
You can find how it is used in this `example <https://github.com/ABM4ALL/CovidNetworkContagionVisual>`_.

We think the introduction of ``environment`` is helpful for two reasons:

* First, the model "timeline" can be summarized in one place - the ``model.run`` function - clearly. Writing the ``step`` function(s) is avoided. Furthermore, it is also easier to include ``sub-steps`` in each ``step``.
* Second, the ``scheduler`` and ``agents`` in **Mesa** and **AgentPy** can iterate through all the agents and call their decision-making functions. However, when there are interactions among agents, for example, when agents randomly pair with each other and play "rock-paper-scissors", the coordination function has to be written in the ``model``. In **Melodie**, all the logics about agents' decision-making and interaction are written in one place - the ``environment`` class.

Finally, the ``DataCollector`` class is also separated and enhanced in **Melodie**.

* First, like in **Mesa** and **AgentPy**, the users can define which variables to be collected (1) at the micro-level from the ``agents``, or (2) at the macro-level from the ``environment``. Then, they will be automatically collected in each period and saved in the database.
* Second, the users can also define functions for parsing specific data structure from the ``agents`` and the ``environment`` and saving them in the database.
* Third, with a ``db`` attribute, the ``data_collector`` can interact with the database easily. **Melodie** uses a ``.sqlite`` database by default. The ``data_collector`` writes the results into the ``.sqlite`` file after each simulation run instead of holding them in the memory.

Scenario Management
___________________

Melodie
~~~~~~~

As introduced in the :ref:`Introduction` and :ref:`Tutorial` sections, in a model developed with **Melodie**:

* First, all the input data are loaded by the ``data_loader`` into the ``scenario`` object. Then, as the input data container, the ``scenario`` object can be accessed by the ``model`` and its components, including ``environment``, ``data_collector``, and each ``agent``.
* Second, **Melodie** provides two standard classes - ``DataFrameInfo`` and ``MatrixInfo`` - with which the users can register the input dataframes and matrices so they can be easily processed by ``DataLoader`` and ``Scenario``.

Together with the ``config`` and ``CovidModel`` class,
the ``CovidScenario`` and ``CovidDataLoader`` classes are used to construct the ``simulator`` (Line 20-21).
Then, by calling the ``run`` function (Line 25),
all the scenarios defined in the ``SimulatorScenario.xlsx`` file are batched and run by the ``simulator``.

.. code-block:: Python
   :caption: run_melodie.py
   :linenos:
   :emphasize-lines: 20-21, 25

   import os

   from Melodie import Config
   from Melodie import Simulator

   from source_melodie.data_loader import CovidDataLoader
   from source_melodie.model import CovidModel
   from source_melodie.scenario import CovidScenario

   config = Config(
       project_name="Melodie_CovidContagion",
       project_root=os.path.dirname(__file__),
       input_folder="data/input",
       output_folder="data/output",
   )

   simulator = Simulator(
       config=config,
       model_cls=CovidModel,
       scenario_cls=CovidScenario,
       data_loader_cls=CovidDataLoader
   )

   if __name__ == "__main__":
       simulator.run()

As the project structure shows, there are three more files in the ``source_melodie`` folder:

* ``data_info.py`` - the users can register the input dataframes and matrices.
* ``data_loader.py`` - the users can load the input dataframes and matrices. Besides, the users can generate scenario-dependent dataframes to initialize the agents. The dataframes are generated and saved in the database automatically. The users can easily use them together with the result dataframes in the analysis after running the model.
* ``scenario.py`` - the users can define the parameters of the scenarios. The parameters should be consistent with the column names in the ``SimulatorScenario.xlsx`` file. Besides, the users can also process the input dataframes (e.g., transforming them into specific data structure) for easier or faster use by the ``model`` and its components.

In the :ref:`Tutorial` section, we explain how the ``data_loader`` and ``scenario`` can be used,
especially (1) "generating scenario-dependent dataframe for initializing agents" in the ``CovidDataLoader`` class,
and (2) "transforming input data into specific data structure for easier use" in the ``CovidScenario`` class.

Mesa
~~~~

In **Mesa**, there is no ``scenario`` object.
The input data is contained in a ``dictionary`` as shown in Line 14 below.
Then, the ``dictionary`` is used to initialize the model (Line 7-10 in ``source_mesa/model``).

.. code-block:: Python
   :caption: run_mesa.py
   :linenos:
   :emphasize-lines: 14

   import os

   import pandas as pd

   from source_mesa.analyzer import plot_result
   from source_mesa.model import CovidModel


   def run_mesa():
       scenarios_df = pd.read_excel(os.path.join('data/input', 'SimulatorScenarios.xlsx'))
       for scenario_params in scenarios_df.to_dict(orient='records'):
           scenario_id = scenario_params.pop('id')
           period_num = scenario_params.pop('period_num')
           model = CovidModel(**scenario_params)
           for i in range(period_num):
               model.step()
           plot_result(model, scenario_id)
           print("=" * 20, f"Scenario {scenario_id} finished", "=" * 20)

.. code-block:: Python
   :caption: source_mesa/model.py
   :linenos:
   :emphasize-lines: 7-10

   import mesa


   class CovidModel(mesa.Model):

       def __init__(self, **kwargs):
           self.num_agents = kwargs["agent_num"]
           self.initial_infected_percentage = kwargs["initial_infected_percentage"]
           self.young_percentage = kwargs["young_percentage"]
           self.infection_prob = kwargs["infection_prob"]

Besides, **Mesa** also has a ``batch_run`` function that can
(1) iterate through the pre-defined scenarios (similar to the ``simulator`` in **Melodie**), or
(2) sweep the parameter space of a given model.

AgentPy
~~~~~~~

In **AgentPy**, the input data is also passed into the ``model`` as a ``dictionary``.
However, there are two main differences compared with **Mesa**:

* First, in Line 12, the ``parameters`` passed into ``ap.Experiment`` (not ``model``) is actually "a list of dictionaries". Because **AgentPy** supports batching scenario runs with the ``Experiment`` module, which is similar to the ``Simulator`` in **Melodie**. They are both at a higher level than ``model``.
* Second, in the ``model``, the ``dictionary`` can be accessed as ``model.p`` whenever needed, not only when initializing the ``model``. In **Melodie**, the ``scenario`` can also be accessed whenever needed. Furthermore, it can be accessed by the ``model`` and all of its components.

.. code-block:: Python
   :caption: run_agentpy.py
   :linenos:
   :emphasize-lines: 12

   import os.path

   import agentpy as ap
   import pandas as pd

   from source_agentpy.analyzer import plot_result
   from source_agentpy.model import CovidModel


   def run_agentpy():
       parameters = pd.read_excel(os.path.join('data/input', 'SimulatorScenarios.xlsx'))
       exp = ap.Experiment(CovidModel, parameters.to_dict('records'))
       results = exp.run()
       plot_result(results['reporters'], parameters)

Summary
~~~~~~~

Regarding the scenario management (data import and preparation),
**Melodie** provides relevant tools (or infrastructure)
- the ``Scenario`` and ``DataLoader`` modules - to smooth the workflow.
Besides, the ``DataFrameInfo`` and ``MatrixInfo`` classes are prepared for easier data processing.
**Melodie** can check automatically if the registries in the ``data_info.py``
are consistent with the input ``.xlsx`` files and the attributes of the ``scenario``.
We think such design is helpful especially when the ``scenario`` includes large and complicated dataset.

Modeling Manager
________________

"Modeling Manager" is a set of classes that **Melodie** provides at a higher level than the ``model``.
The ``Simulator`` module is the first example.
Besides, **Melodie** also provides another two "modeling managers" that are not included in **Mesa** and **AgentPy**:
``Calibrator`` and ``Trainer``.

Calibrator
~~~~~~~~~~

The ``calibrator`` module in **Melodie** can calibrate the scenario parameters of a model by minimizing the
distance between model output and a "target".
The "target" can be defined directly or calculated based on input data.
For example, in the ``CovidCalibrator`` class, the users need to define

* First, the parameter to calibrate, which must be an attribute of the ``scenario`` object (Line 9), which is the ``infection_prob``;
* Second, optionally, some ``environment`` properties that are interesting to look at their evolution in the calibration process (Line 10);
* Third, the ``distance`` between the model output and a pre-defined "target" (Line 12-13), which is the percentage of "uninfected people" in the population by the end of the simulation.

.. code-block:: Python
   :caption: calibrator.py
   :linenos:
   :emphasize-lines: 9-10, 12-13

   from Melodie import Calibrator

   from source.environment import CovidEnvironment


   class CovidCalibrator(Calibrator):

       def setup(self):
           self.add_scenario_calibrating_property("infection_prob")
           self.add_environment_property("s0")

       def distance(self, environment: "CovidEnvironment") -> float:
           return (environment.s0 / environment.scenario.agent_num - 0.5) ** 2

The code above is taken from the :ref:`CovidContagionCalibrator` example.
For details, please read the code and document.
As shown in the figure below, the ``infection_prob`` converges to 0.15 in the calibration process,
which is stable in three calibration runs.

.. image:: /image/calibrator_infection_prob.png

Trainer
~~~~~~~

The ``Trainer`` module in **Melodie** can train the ``agents`` to update their behavioral parameters for higher payoff, individually.
The framework is introduced in detail in `Yu (2020) <https://ieeexplore.ieee.org/document/9857838/>`_:
*An Agent-based Framework for Policy Simulation: Modeling Heterogeneous Behaviors with Modified Sigmoid Function and Evolutionary Training*.

The motivation of ``Trainer`` is to "calibrate" the behavioral parameters for each agent,
especially when the agents are heterogeneous with each other.
However, conceptually, ``Trainer`` is different from ``Calibrator``
because the model validity is not empirically evaluated by the "distance",
but only improved or disciplined by optimization, i.e., evolutionary training.
In other words, the performance requirement for the model validity is not "producing data that are close enough to the observed data",
but "the agents are smart enough to make reasonable decisions".
This is a compromise when simulation-based calibration is not possible due to lack of empirical data at the agent-level.

In the :ref:`RockPaperScissorsTrainer` section,
we provide an example that explains how ``Trainer`` can be used in detail.

