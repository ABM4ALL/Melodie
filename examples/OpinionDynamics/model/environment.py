
import random
import numpy as np
from typing import TYPE_CHECKING

from Melodie import AgentList, Environment
from .scenario import GiniScenario

if TYPE_CHECKING:
    from .agent import GiniAgent


class GiniEnvironment(Environment):
    scenario: GiniScenario

    def setup(self):
        self.trade_num = self.scenario.trade_num
        self.win_prob = self.scenario.rich_win_prob
        self.total_wealth = 0
        self.gini = 0

    def go_money_produce(self, agent_list):

        for agent in agent_list:
            agent.go_produce()

        return None

    def go_give_money(self, agent_from: 'GiniAgent', agent_to: 'GiniAgent'):

        if agent_from.account == 0:
            pass
        else:
            agent_from.account -= 1
            agent_to.account += 1

        return None

    def go_money_transfer(self, agent_list: 'AgentList'):
        for sub_period in range(0, self.trade_num):
            [agent_1, agent_2] = agent_list.random_sample(2)

            who_win = ''
            rand = random.random()
            if rand <= self.win_prob:
                who_win = 'Rich'
            else:
                who_win = 'Poor'

            if agent_1.account >= agent_2.account and who_win == 'Rich':
                self.go_give_money(agent_2, agent_1)
            elif agent_1.account < agent_2.account and who_win == 'Rich':
                self.go_give_money(agent_1, agent_2)
            elif agent_1.account >= agent_2.account and who_win == 'Poor':
                self.go_give_money(agent_1, agent_2)
            elif agent_1.account < agent_2.account and who_win == 'Poor':
                self.go_give_money(agent_2, agent_1)
            else:
                pass

        return None

    def calc_gini(self, Account_list):

        x = sorted(Account_list)
        N = len(Account_list)
        B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * sum(x))

        return (1 + (1 / N) - 2 * B)

    def calc_wealth_and_gini(self, AgentList):

        account_list = []
        for agent in AgentList:
            account_list.append(agent.account)

        self.total_wealth = sum(account_list)
        self.gini = self.calc_gini(account_list)

        return None




class PandoraModel(Environment):
    """A model with some number of agents.
    self.regression_coefficients: Values define Matrix size for the PolicyAgent within the deliberative processing mode
                                  --> policy info attributes (12) + influencing factors (environmental and political concern) on policy evaluation (2)
    """
    def __init__(self, N):
        self.regression_coefficients = np.random.rand(14, 3)
        self.policy_info = np.array([
            100,0,0,
            1,0,0,
            1,0,0,
            1,0,0])

        self.num_agents = N
        self.schedule = RandomFractionActivation(self, 0.3)  # Fraction of agents is activated in each step

        # Create agents
        for i in range(self.num_agents):
            agent_properties = self._get_random_agent_properties()
            agent = PolicyAgent(i, self, agent_properties)
            self.schedule.add(agent)

            # With 20% chance receive global info on agent creation (preliminary random assumption, will depend on further parameters):
            if random.random() < 0.2:
                agent.process_policy_info(self.policy_info)
                print(agent.unique_id, agent.get_attitude_vector())

    def _get_random_agent_properties(self):
        return {
            'political_interest': random.randint(-3,3),
            'technology_interest': random.randint(-3,3),
            'house_owner': random.randint(0,1) == 1,
            'environmental_attitude': random.randint(-3,3),
            'political_attitude': random.randint(-3,3),
            'expectancy_fairness': random.uniform(0,1),
            'expectancy_financial_burden': random.uniform(0,1),
            'expectancy_effectiveness': random.uniform(0,1)}

    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()