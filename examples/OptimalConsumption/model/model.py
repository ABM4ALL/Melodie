
from Melodie import Model, AgentList
from .scenario import OCScenario
from .agent import OCAgent
from .environment import OCEnvironment
from .data_collector import OCDataCollector


class OCModel(Model):
    scenario: OCScenario
    
    def setup(self):

        self.agent_list: AgentList[OCAgent] = self.create_agent_container(
            OCAgent,
            self.scenario.agent_num,
            self.scenario.get_registered_dataframe('agent_params')
        )

        with self.define_basic_components():
            self.environment = OCEnvironment()
            self.data_collector = OCDataCollector()

    def run(self):
        self.environment.setup_agents_action_probability(self.agent_list)
        for t in range(0, self.scenario.periods):
            print(f'Period = {t}')
            self.environment.run_game_rounds(self.agent_list)
            self.environment.calc_agents_total_account(self.agent_list)
            self.data_collector.collect(t)
        self.data_collector.save()

