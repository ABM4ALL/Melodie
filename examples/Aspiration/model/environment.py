
import numpy as np
from typing import Type, List, TYPE_CHECKING
from Melodie import Environment
from .scenario import AspirationScenario
from .market_strategy import MarketStrategy, NonCompetitiveMarketStrategy

if TYPE_CHECKING:
    from .agent import AspirationAgent


class AspirationEnvironment(Environment):

    def setup(self):
        scenario: AspirationScenario = self.current_scenario()
        self.market_strategy = scenario.market_strategy
        self.market_profit_mean = scenario.market_profit_mean
        self.market_profit_sigma = scenario.market_profit_sigma
        self.sigma_exploitation = scenario.sigma_exploitation
        self.mean_exploration = scenario.mean_exploration
        self.sigma_exploration = scenario.sigma_exploration
        self.imitation_share = scenario.imitation_share
        self.imitation_success_rate = scenario.imitation_success_rate
        self.average_technology = 0.0

    def market_strategy_choice(self) -> Type[MarketStrategy]:
        if self.market_strategy == 0:
            return NonCompetitiveMarketStrategy
        else:
            pass

    def market_process(self, agent_list: 'List[AspirationAgent]') -> None:
        market_strategy = self.market_strategy_choice()(agent_list, self)
        for agent in agent_list:
            market_strategy.calculate_profit(agent)
        pass

    def aspiration_update_process(self, agent_list: 'List[AspirationAgent]') -> None:
        for agent in agent_list:
            aspiration_update_strategy = agent.aspiration_update_strategy_choice()
            aspiration_update_strategy(agent_list, self).aspiration_update(agent)
        pass

    def technology_search_process(self, agent_list: 'List[AspirationAgent]') -> None:
        for agent in agent_list:
            technology_search_strategy = agent.technology_search_strategy_choice()
            technology_search_strategy(agent_list, self).technology_search(agent)
        pass

    def calculate_environment_result(self, agent_list: 'List[AspirationAgent]') -> None:
        self.average_technology = np.array([agent.technology for agent in agent_list]).mean()


