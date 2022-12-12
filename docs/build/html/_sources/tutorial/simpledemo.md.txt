Simplest Demo
=======================

It is believed that learning by an example is better than by viewing the function list of Melodie. So this example is a
simple demonstration of Gini index.

This example explores how "Gini index" can be influenced by the productivity of and equality among people. After
initialization, each agents get some money in their account. Then, in each period, all the agents go through following
two processes:

- MoneyProduce: randomly receive some money.
- MoneyTransfer: in each period, there are multiple rounds (sub-periods). In each round, two agents are randomly
  selected and they play a game. The winner will take 1 dollar from the loser.

The system calculates the "total wealth" and "gini index" in each period.

There are two key parameters to discuss in the example:

- Productivity: the probability of agents to successfully produce some money at the beginning of each period.
- Winning probability of richer player: in each game between two randomly selected players, the result is
  probabilistically decided by a pre-defined parameter, i.e. the probability that the richer player will win the game.
  With this parameter, we introduce "allocation equality" in the model

By changing these two parameters, we can explore the following question: how is the "Gini index" influenced by the
productivity and equality in the society.

## Define the Agent

```python

import random

from Melodie import Agent
from .scenario import GiniScenario


class GiniAgent(Agent):
    scenario: GiniScenario

    def setup(self):
        self.account = .0
        self.productivity = .0

    def go_produce(self):
        rand = random.random()
        if rand <= self.productivity:
            self.account += self.scenario.agent_productivity
        else:
            pass

        return None

```

## Define the Scenario

```python
from Melodie import Scenario


class GiniScenario(Scenario):
    def setup(self):
        self.periods = 100
        self.agent_num = 0
        self.agent_account_min = 0.0
        self.agent_account_max = 0.0
        self.agent_productivity = 0.0
        self.trade_num = 0
        self.rich_win_prob = 0.0
```

## Define the Environment

```python

import random
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
```

## Define the Model

```python
from Melodie import Model

class GiniModel(Model):
    scenario: 'GiniScenario'
    environment: 'GiniEnvironment'

    def setup(self):
        self.agent_list = self.create_agent_container(GiniAgent, self.scenario.agent_num,
                                                      self.scenario.get_registered_dataframe('agent_params'))

        with self.define_basic_components():
            self.environment = GiniEnvironment()
            self.data_collector = GiniDataCollector()

    def run(self):
        # for t in range(0, self.scenario.periods):
        for step in self.routine():
            self.environment.go_money_produce(self.agent_list)
            self.environment.go_money_transfer(self.agent_list)
            self.environment.calc_wealth_and_gini(self.agent_list)
            self.data_collector.collect(step - 1)
            print('step', step, self.scenario.agent_productivity)
        self.data_collector.save()

```

## Load DataFrames

```python
import sqlalchemy

from Melodie import DataFrameLoader


class GiniDataframeLoader(DataFrameLoader):

    def register_scenario_dataframe(self):
        scenarios_dict = {}
        self.load_dataframe('simulator_scenarios', 'simulator_scenarios.xlsx', scenarios_dict)

    def register_generated_dataframes(self):
        with self.table_generator('agent_params', lambda scenario: scenario.agent_num) as g:
            def generator_func(scenario: "GiniScenario"):
                return {
                    'id': g.increment(),
                    'productivity': scenario.agent_productivity,
                    'account': 0.0
                }

            g.set_row_generator(generator_func)
            g.set_column_data_types({
                'id': sqlalchemy.Integer(),
                'productivity': sqlalchemy.Float(),
                'account': sqlalchemy.Float()
            })

```

## Collect Data

```python

from Melodie import DataCollector


class GiniDataCollector(DataCollector):
    def setup(self):
        self.add_agent_property('agent_list', 'account')
        self.add_environment_property('trade_num')
        self.add_environment_property('win_prob')
        self.add_environment_property('total_wealth')
        self.add_environment_property('gini')
```

## Run Example

```python
simulator = Simulator(config=config,
                      scenario_cls=GiniScenario,
                      model_cls=GiniModel,
                      df_loader_cls=GiniDataframeLoader)

simulator.run()
```
