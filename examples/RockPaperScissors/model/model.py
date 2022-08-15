import time

from Melodie import Model, AgentList
from .scenario import RPSScenario
from .agent import RPSAgent
from .environment import RPSEnvironment
from .data_collector import RPSDataCollector


class RPSModel(Model):
    scenario: RPSScenario

    def setup(self):

        self.agent_list: AgentList[RPSAgent] = self.create_agent_container(
            RPSAgent,
            self.scenario.agent_num,
            self.scenario.get_dataframe("agent_params"),
        )

        with self.define_basic_components():
            self.environment = RPSEnvironment()
            self.data_collector = RPSDataCollector()

    def run(self):
        self.environment.setup_agents_action_probability(self.agent_list)
        for t in range(0, self.scenario.period_num):
            self.environment.run_game_rounds(self.agent_list)
            self.environment.calc_agents_total_account(self.agent_list)
