from typing import TYPE_CHECKING
from Melodie import AgentList
from tutorial.CovidContagion.model import data_info as df_info

if TYPE_CHECKING:
    from Melodie import AgentList
    from .scenario import CovidScenario
    from .grid import CovidGrid
    from .network import CovidNetwork


class CovidAgentList(AgentList):
    scenario: CovidScenario

    def setup(self):
        self.set_agent_num(self.scenario.agent_num)
        self.set_agent_params(self.scenario.get_dataframe(df_info.agent_params))
