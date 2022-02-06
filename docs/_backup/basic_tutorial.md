# Basic Tutorial

## A Basic Tutorial of Gini Index

### Introduction

*This is a simple demonstration within one page for beginner to quickly get familiar of Melodie. We suggest developers
modelling in separate files.*

In this model, we will build a virtual economy and simulate how the gini index changes when the economy develops.

At the beginning, all agents has no money. Then, for each step, this model will act following these rules:

1. Each agent produces 1 dollar.
2. Randomly select two Agents. For the probability `rich_win_prob`, the poorer agent will give 1 dollar to the richer.
   This rule is performed in each step for `trade_num` times.

The rules are often be described by a method of Environment or Agent.

### Build `Agent`

```python
__author__ = 'Songmin'

from Melodie import Agent


class GiniAgent(Agent):

    def setup(self):
        self.account = .0  # initialize `account` with type float

    def go_produce(self):
        self.account += 1
```

Here is how we model the agent. Modelling the agent takes these simple steps:

1. Write a custom class inheriting `Melodie.Agent`. It is suggested to name this class with the suffix of `Agent`.
2. Rewrite the `setup()` method, and define the properties inside this method.
    - In the above piece of code, we defined the property `GiniAgent.account`, and initiated it with value 0,
      type `float`.
    - If the initial value cannot be determined in `setup()`, we still need a initial value. Use `0` for `int`, `.0`
      for `float`, `''` for `str` and `False` for `boolean`.
4. Add custom methods such as `go_produce`.
    - WARNING: DO NOT define new properties in methods except `setup`!

### Build the `Environment`

For Melodie framework, the Environment always plays the key role when modelling. If a rule involves interactions of more
than 1 agent, this rule is suggested to be written as the Environment method.

```python
import random
from Melodie import Environment


class GiniEnvironment(Environment):

    def setup(self):
        self.trade_num = 200
        self.rich_win_prob = 0.8
        self.total_wealth = 0
        self.gini = 0

    def go_money_produce(self, agent_list):
        for agent in agent_list:
            agent.go_produce()

    def go_give_money(self, agent_from: 'GiniAgent', agent_to: 'GiniAgent'):
        if agent_from.account <= 1:
            pass
        else:
            agent_from.account -= 1
            agent_to.account += 1

    def go_money_transfer(self, agent_list: 'AgentList'):
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

    def step(self, agent_list: 'AgentList[GiniAgent]'):
        self.go_money_produce(agent_list)
        self.go_money_transfer(agent_list)
        self.calc_wealth_and_gini(agent_list)
```

In each step, the method of `GiniEnvironment.step` will be executed.

Inside `step()`, the environment executes these methods:

- `GiniEnvironment.go_money_produce`: activate each agent to produce money
- `GiniEnvironment.go_money_transfer`: let the agents to transfer money to each other.
- `GiniEnvironment.calc_wealth_and_gini`:  calculate gini index and total wealth at the end of step.

You may find it different (and sometimes confusing) when noticing each method parameter has special marks such
as `agent_list: AgentList[GiniAgent]`. The mark `AgentList[GiniAgent]` is the annotation to declare the type of
parameter `agent_list`.

`AgentList` is like a list of Agent, though in fact it is not an instance of builtin `list`, but it can be iterated by
for-loop, or index like a list.

The type annotations can be briefly (and not completely) summarized below:

- `int`, `float`, `bool` and `str` reveals that the parameter is type `int`/`float`/`bool`/`str`.
- `GiniAgent` means this parameter stands for a `GiniAgent` object
- `AgentList[GiniAgent]` means this parameter a `AgentList` container object, and its each element is GiniAgent object.

Within these steps of building up Agent and Environment, the major algorithms is completed. But please wait a minute.
Before pasting the code into your editor, there are a few--and only a few--steps to do.

### Setup `DataCollector`

```python
from Melodie import DataCollector


class GiniDataCollector(DataCollector):
    def setup(self):
        self.add_agent_property("agent_list", 'account')
        self.add_environment_property('trade_num')
        self.add_environment_property('rich_win_prob')
        self.add_environment_property('total_wealth')
        self.add_environment_property('gini')
```

`Melodie.DataCollector` is used for collecting data when the model is running. Like `Agent` or `Environment`, defining
the property inside `setup` is required.

- call `add_agent_property(agent_container_name, agent_property)` to collect agent data. The first argument `agent_list`
  should be defined in `Model`.
- call `add_environment_property(environment_property)` to collect environment data.

### Setup `Model`

```python
from Melodie import Model


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
```

1. create the `agent_list` by `Model.create_agent_container`.
2. Use a `with` block to define environment and data_collector. When the with block finishes, it will ensure
   that `self.environment` is not None.

Notice that the property `agent_list` is not compulsory to be named as it, but the `environment` and `data_collector` is
compulsory. There can be more than 1 agent container in a Model, but the `Environment` and `DataCollector` can be only
one.

the `run` method defines the Model routine.

### Define `Simulator` and run this model

```python
import os
from typing import List
from Melodie import Simulator, Scenario, Config


class GiniSimulator(Simulator):
    def register_scenario_dataframe(self):
        scenarios_dict = {}

    def generate_scenarios(self) -> List['Scenario']:
        scenario = Scenario(0)
        scenario.manager = self
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

```

Now the model is built, we could run this example for simple use.

### Complete Code

```python
__author__ = 'Songmin'

import os
import random
from typing import List

from Melodie import Config, Agent, Model, DataCollector, Simulator, Scenario, AgentList, Environment


class GiniAgent(Agent):

    def setup(self):
        self.account = .0  # initialize `account` with type float

    def go_produce(self):
        self.account += 1


class GiniEnvironment(Environment):

    def setup(self):
        self.trade_num = 200
        self.rich_win_prob = 0.8
        self.total_wealth = 0
        self.gini = 0

    def go_money_produce(self, agent_list):
        for agent in agent_list:
            agent.go_produce()

    def go_give_money(self, agent_from: 'GiniAgent', agent_to: 'GiniAgent'):
        if agent_from.account <= 1:
            pass
        else:
            agent_from.account -= 1
            agent_to.account += 1

    def go_money_transfer(self, agent_list: 'AgentList'):
        for sub_period in range(0, self.trade_num):
            [agent_1, agent_2] = agent_list.random_sample(2)
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

    def calc_gini(self, Account_list):
        x = sorted(Account_list)
        N = len(Account_list)
        if sum(x) == 0:
            return 0
        B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * sum(x))
        return (1 + (1 / N) - 2 * B)

    def calc_wealth_and_gini(self, AgentList):

        account_list = []
        for agent in AgentList:
            account_list.append(agent.account)

        self.total_wealth = sum(account_list)
        self.gini = self.calc_gini(account_list)

        return None


class GiniModel(Model):

    def setup(self):
        self.agent_list = self.create_agent_container(GiniAgent, 100)
        with self.define_basic_components():
            self.environment = GiniEnvironment()
            self.data_collector = GiniDataCollector()

    def run(self):
        for t in range(0, self.scenario.periods):
            self.environment.go_money_produce(self.agent_list)
            self.environment.go_money_transfer(self.agent_list)
            self.environment.calc_wealth_and_gini(self.agent_list)
            self.data_collector.collect(t)
        self.data_collector.save()


class GiniDataCollector(DataCollector):
    def setup(self):
        self.add_agent_property("agent_list", 'account')
        self.add_environment_property('trade_num')
        self.add_environment_property('rich_win_prob')
        self.add_environment_property('total_wealth')
        self.add_environment_property('gini')


class GiniSimulator(Simulator):
    def register_scenario_dataframe(self):
        scenarios_dict = {}

    def generate_scenarios(self) -> List['Scenario']:
        scenario = Scenario(0)
        scenario.manager = self
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
```