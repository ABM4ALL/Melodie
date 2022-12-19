
CovidNetworkContagion
=======================

To show how the ``Melodie.Network`` module can be used,
we provide this `CovidNetworkContagion <https://github.com/ABM4ALL/CovidNetworkContagion>`_ model,
which is based the `CovidContagion <https://github.com/ABM4ALL/CovidContagion>`_ model.
So, if you haven't, we will strongly suggest to read the :ref:`Tutorial` section first.

The differences are:

* Agents are connected within a ``network`` randomly.
* The ``network`` is constructed with edges, representing the connections between the agents. An infected agent can pass the virus through the edge to another uninfected agent.

Project Structure
_________________

The project structure is as follows.

::

    CovidNetworkContagion
    ├── data
    │   ├── input
    │   │   ├── SimulatorScenarios.xlsx
    │   │   ├── ID_HealthState.xlsx
    │   │   ├── ID_AgeGroup.xlsx
    │   │   └── Parameter_AgeGroup_TransitionProb.xlsx
    │   └── output
    │       ├── CovidGridContagion.sqlite
    │       ├── PopulationInfection_S0R0.png
    │       └── PopulationInfection_S1R0.png
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

Model
_____

As shown in the project structure, unlike :ref:`CovidGridContagion`,
it is same with the structure of the `CovidContagion <https://github.com/ABM4ALL/CovidContagion>`_ model.
Because the edges in the ``network`` do not store model-specific parameters like spots in the ``grid``.
The ``network`` only provide common functions.

So, by calling the ``create_network`` function (Line 22) without passing any parameters,
the ``network`` component is created for the model with the default classes in ``Melodie``.

.. code-block:: Python
   :caption: model.py
   :linenos:
   :emphasize-lines: 22, 29-33

   from typing import TYPE_CHECKING

   from Melodie import Model

   from source import data_info
   from source.agent import CovidAgent
   from source.data_collector import CovidDataCollector
   from source.environment import CovidEnvironment
   from source.scenario import CovidScenario

   if TYPE_CHECKING:
       from Melodie import AgentList


   class CovidModel(Model):
       scenario: "CovidScenario"

       def create(self):
           self.agents: "AgentList[CovidAgent]" = self.create_agent_list(CovidAgent)
           self.environment = self.create_environment(CovidEnvironment)
           self.data_collector = self.create_data_collector(CovidDataCollector)
           self.network = self.create_network()

       def setup(self):
           self.agents.setup_agents(
               agents_num=self.scenario.agent_num,
               params_df=self.scenario.get_dataframe(data_info.agent_params),
           )
           self.network.setup_agent_connections(
               agent_lists=[self.agents],
               network_type=self.scenario.network_type,
               network_params=self.scenario.get_network_params(),
           )

Then, the ``network`` needs to be setup based on

* ``agent_lists`` - a list of ``agents``, i.e., multiple groups of ``agents`` can be connected in the same network. They are distinguished by the ``category`` attribute as in the :ref:`CovidGridContagion` model.
* ``network_type`` and ``network_params`` - follows the tradition of ``NetworkX`` package, because the ``Melodie.Network`` module is developed highly based on it.

Scenario
________

The parameters to setup the ``network`` could be inserted into the model through ``scenario``.

.. code-block:: Python
   :caption: scenario.py
   :linenos:
   :emphasize-lines: 10-13, 19

   from Melodie import Scenario
   from source import data_info


   class CovidScenario(Scenario):

       def setup(self):
           self.period_num: int = 0
           self.agent_num: int = 0
           self.network_type: str = ""
           self.network_param_k: int = 0
           self.network_param_p: float = 0.0
           self.network_param_m: int = 0
           self.initial_infected_percentage: float = 0.0
           self.young_percentage: float = 0.0
           self.infection_prob: float = 0.0
           self.setup_transition_probs()

       def get_network_params(self):
           if self.network_type == "barabasi_albert_graph":
               network_params = {"m": self.network_param_m}
           elif self.network_type == "watts_strogatz_graph":
               network_params = {"k": self.network_param_k, "p": self.network_param_p}
           else:
               raise NotImplementedError
           return network_params

For more details of the ``Network`` module, please refer to the :ref:`API Reference` section.

















