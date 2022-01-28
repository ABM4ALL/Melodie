__author__ = 'Songmin'

import os
import random
from typing import List

from Melodie import Config, Agent, Model, DataCollector, Simulator, Scenario, AgentList, Environment


class GiniAgent(Agent):

    def setup(self):
        self.account = .0  # initialize `account` with type float
        self.productivity = 0.1  # value could be: [0.1, 0.2, 0.5, 1.0, 1.5, 2.0 ]

    def go_produce(self):
        self.account += self.productivity


class GiniEnvironment(Environment):

    def setup(self):
        self.trade_num = 200
        self.rich_win_prob = 0.8
        self.total_wealth = 0
        self.gini = 0

    def go_money_produce(self, agent_list: 'AgentList[GiniAgent]'):
        for agent in agent_list:
            agent.go_produce()

    def go_give_money(self, agent_from: 'GiniAgent', agent_to: 'GiniAgent'):
        if agent_from.account <= 1:
            pass
        else:
            agent_from.account -= 1
            agent_to.account += 1

    def go_money_transfer(self, agent_list: 'AgentList[GiniAgent]'):
        for sub_period in range(0, self.trade_num):
            agent_1, agent_2 = agent_list.random_sample(2)
            who_win = ''
            rand = random.random()
            if rand <= self.rich_win_prob:
                who_win = "Rich"
            else:
                who_win = "Poor"
            if who_win == "Rich":
                if agent_1.account >= agent_2.account:
                    self.go_give_money(agent_2, agent_1)
                else:
                    self.go_give_money(agent_1, agent_2)
            else:
                if agent_1.account <= agent_2.account:
                    self.go_give_money(agent_2, agent_1)
                else:
                    self.go_give_money(agent_1, agent_2)

    def calc_gini(self, account_list):
        x = sorted(account_list)
        N = len(account_list)
        account_sum = sum(x)
        if account_sum == 0:
            return 0
        B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * account_sum)
        return 1 + (1 / N) - 2 * B

    def calc_wealth_and_gini(self, AgentList):
        account_list = []
        for agent in AgentList:
            account_list.append(agent.account)
        self.total_wealth = sum(account_list)
        self.gini = self.calc_gini(account_list)

    def step(self, agent_list: AgentList[GiniAgent]):
        self.go_money_produce(agent_list)
        self.go_money_transfer(agent_list)
        self.calc_wealth_and_gini(agent_list)


class GiniModel(Model):

    def setup(self):
        self.agent_list = self.create_agent_container(GiniAgent, 100)
        with self.define_basic_components():
            self.environment = GiniEnvironment()
            self.data_collector = GiniDataCollector()

    def run(self):
        for t in range(0, self.scenario.periods):
            self.environment.step(self.agent_list)
            self.data_collector.collect(t)
        self.data_collector.save()


class GiniDataCollector(DataCollector):
    def setup(self):
        # self.add_agent_property("agent_list", 'account')
        self.add_environment_property('trade_num')
        self.add_environment_property('rich_win_prob')
        self.add_environment_property('total_wealth')
        self.add_environment_property('gini')


class GiniSimulator(Simulator):
    def generate_scenarios(self) -> List['Scenario']:
        scenario = Scenario(0)
        scenario.manager = self
        scenario.number_of_run = 20
        scenario.periods = 200  # The model will be executed by 100 steps.
        return [scenario]


config = Config(
    project_name='WealthDistribution',
    project_root=os.path.dirname(__file__),
    sqlite_folder='.',
    excel_source_folder='.',
    output_folder='.',
)

simulator = GiniSimulator()

simulator.run(
    config=config,
    model_class=GiniModel,
)
