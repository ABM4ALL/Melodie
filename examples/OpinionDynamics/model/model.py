from typing import TYPE_CHECKING
from Melodie import Model, Network
from .agent import OpinionDynamicsAgent
from .environment import OpinionDynamicsEnvironment
from .data_collector import OpinionDynamicsDataCollector

if TYPE_CHECKING:
    from .scenario import OpinionDynamicsScenario


class OpinionDynamicsModel(Model):
    scenario: "OpinionDynamicsScenario"

    def setup(self):
        self.agent_list = self.create_agent_container(
            OpinionDynamicsAgent,
            self.scenario.agent_num,
            self.scenario.get_dataframe("agent_params"),
        )

        with self.define_basic_components():
            self.environment = OpinionDynamicsEnvironment()
            self.network = Network.from_agent_containers(
                {"agent_list": self.agent_list},
                "watts_strogatz_graph",
                {
                    "k": self.scenario.network_param_k,
                    "p": self.scenario.network_param_p,
                },
            )
            self.data_collector = OpinionDynamicsDataCollector()

    def run(self):
        for t in range(0, self.scenario.periods):
            print(f"period = {t}")
            self.environment.agents_communication(self.agent_list, self.network)
            self.environment.calc_average_opinion_level(self.agent_list)
            self.data_collector.collect(t)
        self.data_collector.save()
