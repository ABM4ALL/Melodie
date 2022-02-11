from typing import Type
from Melodie import Environment, AgentList
from .agent import AspirationAgent
from .scenario import AspirationScenario
from .market_strategy import MarketStrategy, NonCompetitiveMarketStrategy


class AspirationEnvironment(Environment):
    scenario: AspirationScenario

    def setup(self):
        self.average_technology = 0.0
        self.account_total = 0.0
        self.sleep_accumulated_share = 0
        self.exploration_accumulated_share = 0
        self.exploitation_accumulated_share = 0
        self.imitation_accumulated_share = 0

    def agent_post_setup(self, agent_list: 'AgentList[AspirationAgent]') -> None:
        for agent in agent_list:
            agent.post_setup()

    def market_strategy_choice(self) -> Type[MarketStrategy]:
        if self.scenario.market_strategy == 0:
            return NonCompetitiveMarketStrategy
        else:
            pass

    def market_process(self, agent_list: 'AgentList[AspirationAgent]') -> None:
        market_strategy = self.market_strategy_choice()(agent_list, self)
        for agent in agent_list:
            market_strategy.calculate_profit(agent)
        pass

    def aspiration_update_process(self, agent_list: 'AgentList[AspirationAgent]') -> None:
        for agent in agent_list:
            aspiration_update_strategy = agent.aspiration_update_strategy_choice()
            aspiration_update_strategy(agent_list, self).aspiration_update(agent)
        pass

    def technology_search_process(self, agent_list: 'AgentList[AspirationAgent]') -> None:
        for agent in agent_list:
            technology_search_strategy = agent.technology_search_strategy_choice()
            technology_search_strategy(agent_list, self).technology_search(agent)
        pass

    def calculate_average_technology(self, agent_list: 'AgentList[AspirationAgent]') -> None:
        sum_tech = 0
        for agent in agent_list:
            sum_tech += agent.technology
        self.average_technology = sum_tech / len(agent_list)

    def calculate_account_total(self, agent_list: 'AgentList[AspirationAgent]') -> None:
        for agent in agent_list:
            self.account_total += agent.account

    def calculate_technology_search_strategy_share(self, agent_list: 'AgentList[AspirationAgent]') -> None:
        total_sleep_count = 0
        total_exploration_count = 0
        total_exploitation_count = 0
        total_imitation_count = 0
        for agent in agent_list:
            total_sleep_count += agent.sleep_count
            total_exploration_count += agent.exploration_count
            total_exploitation_count += agent.exploitation_count
            total_imitation_count += agent.imitation_count
        count_sum = total_sleep_count + total_exploration_count + total_exploitation_count + total_imitation_count
        self.sleep_accumulated_share = total_sleep_count / count_sum
        self.exploration_accumulated_share = total_exploration_count / count_sum
        self.exploitation_accumulated_share = total_exploitation_count / count_sum
        self.imitation_accumulated_share = total_imitation_count / count_sum
