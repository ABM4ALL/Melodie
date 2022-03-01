
from typing import Type
import random
import numpy as np

from Melodie import Environment, AgentList
from .agent import AspirationAgent
from .scenario import AspirationScenario


class AspirationEnvironment(Environment):
    scenario: AspirationScenario

    def setup(self):
        self.average_technology = 0.0
        self.average_account = 0.0
        self.sleep_accumulated_share = 0
        self.exploration_accumulated_share = 0
        self.exploitation_accumulated_share = 0
        self.imitation_accumulated_share = 0

    def agent_post_setup(self, agent_list: 'AgentList[AspirationAgent]') -> None:
        for agent in agent_list:
            agent.post_setup()

    def market_process(self, agent_list: 'AgentList[AspirationAgent]') -> None:
        mean = self.scenario.market_profit_mean
        sigma = self.scenario.market_profit_sigma
        for agent in agent_list:
            agent.profit = agent.technology + np.random.normal(mean, sigma)
            agent.account += agent.profit
            agent.profit_aspiration_difference = agent.profit - agent.aspiration_level

    def aspiration_update_process(self, agent_list: 'AgentList[AspirationAgent]') -> None:
        average_profit = np.array([agent.profit for agent in agent_list]).mean()
        for agent in agent_list:
            if agent.aspiration_update_strategy == 0:
                agent.aspiration_update_historical_strategy()
            elif agent.aspiration_update_strategy == 1:
                agent.aspiration_update_social_strategy(average_profit)
            else:
                pass

    def technology_search_process(self, agent_list: 'AgentList[AspirationAgent]') -> None:
        agent_technology_list = [(agent.id, agent.technology, agent.profit) for agent in agent_list]
        for agent in agent_list:
            if agent.profit_aspiration_difference >= 0:
                agent.technology_search_sleep_strategy()
            else:
                rand = np.random.uniform(0, 1)
                if rand <= agent.prob_exploration:
                    agent.technology_search_exploration_strategy()
                elif agent.prob_exploration < rand <= agent.prob_exploration + agent.prob_exploitation:
                    agent.technology_search_exploitation_strategy()
                else:
                    agent.imitation_count += 1
                    agent.account -= self.scenario.cost_imitation
                    observation_num = int(len(agent_list) * self.scenario.imitation_share)
                    observable_technology_list = random.sample(agent_technology_list, observation_num)
                    observable_technology_list_rank = sorted(
                        observable_technology_list,
                        key=lambda x: x[2],
                        reverse=True
                    )

                    teacher_pos = 0
                    if observable_technology_list_rank[0][0] == agent.id:
                        teacher_pos = 1
                    else:
                        pass
                    teacher_id = observable_technology_list_rank[teacher_pos][0]
                    teacher_technology = observable_technology_list_rank[teacher_pos][1]
                    agent_list[teacher_id].account += self.scenario.cost_imitation
                    agent_list[teacher_id].be_learned_count += 1

                    rand = np.random.uniform(0, 1)
                    if rand <= (1 - self.scenario.imitation_fail_rate):
                        agent.technology = max(agent.technology, teacher_technology)
                    else:
                        pass

    def calculate_average_technology(self, agent_list: 'AgentList[AspirationAgent]') -> None:
        sum_tech = 0
        for agent in agent_list:
            sum_tech += agent.technology
        self.average_technology = sum_tech / len(agent_list)

    def calculate_account_total(self, agent_list: 'AgentList[AspirationAgent]') -> None:
        sum_account = 0
        for agent in agent_list:
            sum_account += agent.account
        self.average_account = sum_account / len(agent_list)

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


