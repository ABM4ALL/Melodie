
from typing import TYPE_CHECKING
import random
from Melodie import Environment

if TYPE_CHECKING:
    from Melodie import AgentList
    from .agent import OCAgent
    from .scenario import OCScenario


class OCEnvironment(Environment):
    scenario: 'OCScenario'

    def setup(self):
        self.agents_total_payoff = 0.0

    def setup_agents_action_probability(self, agent_list: 'AgentList[OCAgent]') -> None:
        for agent in agent_list:
            agent.setup_action_probability()

    def run_game_rounds(self, agent_list: 'AgentList[OCAgent]') -> None:
        assert len(agent_list)%2 == 0, print("scenario.agent_num must be even number.")
        agent_id_list = [i for i in range(0, len(agent_list))]
        random.shuffle(agent_id_list)
        while agent_id_list:
            agent_1 = agent_list[agent_id_list.pop()]
            agent_2 = agent_list[agent_id_list.pop()]
            self.agents_battle(agent_1, agent_2)

    def agents_battle(self, agent_1: 'OCAgent', agent_2: 'OCAgent'):
        agent_1.period_competitor_id = agent_2.id
        agent_1.action_choice()
        agent_2.period_competitor_id = agent_1.id
        agent_2.action_choice()

        if agent_1.period_action == agent_2.period_action:
            agent_1.update_account_tie()
            agent_2.update_account_tie()
        elif ((agent_1.period_action < agent_2.period_action) and (agent_2.period_action - agent_1.period_action == 1))\
             or (agent_1.period_action - agent_2.period_action == 2):
            agent_1.update_account_lose()
            agent_2.update_account_win()
        elif ((agent_2.period_action < agent_1.period_action) and (agent_1.period_action - agent_2.period_action == 1))\
             or (agent_2.period_action - agent_1.period_action == 2):
            agent_1.update_account_win()
            agent_2.update_account_lose()

    def calc_agents_total_account(self, agent_list: 'AgentList[OCAgent]') -> None:
        for agent in agent_list:
            self.agents_total_payoff += agent.total_payoff













