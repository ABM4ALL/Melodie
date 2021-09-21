from typing import ClassVar

from .agent import Agent
from .agent_manager import AgentManager
from .datacollector import DataCollector
from .environment import Environment
from .scenariomanager import Scenario
from .table_generator import TableGenerator
from .db import DB


class Model:
    def __init__(self, proj_name: str, agent_class: ClassVar[Agent],
                 environment_class: ClassVar[Environment],
                 data_collector_class: ClassVar[DataCollector] = None,
                 table_generator_class: ClassVar[TableGenerator] = None,
                 scenario: Scenario = None):
        self.proj_name = proj_name
        self.agent_class = agent_class
        self.scenario = scenario
        self.environment = environment_class()
        self.agent_manager: AgentManager = None

        if callable(data_collector_class) and issubclass(data_collector_class, DataCollector):
            data_collector = data_collector_class()
            data_collector.setup()
        elif data_collector_class is None:
            data_collector = None
        else:
            raise TypeError(data_collector_class)
        self.data_collector = data_collector

        self.table_generator: TableGenerator = table_generator_class(proj_name, self.scenario)
        self.table_generator.setup()
        self.table_generator.run()

    def setup_agent_manager(self):

        agent_para_data_frame = DB(self.proj_name).read_dataframe('agent_params')
        agent_manager = AgentManager(self.agent_class, self.scenario.agent_num)
        self.agent_manager = agent_manager
        reserved_param_names = ['id']
        param_names = reserved_param_names + [param[0] for param in self.table_generator.agent_params]
        # print(param_names)
        for i, agent in enumerate(agent_manager.agents):
            params = {}
            for agent_param_name in param_names:
                params[agent_param_name] = agent_para_data_frame.iloc[i][agent_param_name]
            agent.set_params(params)
        return agent_manager

    def _setup(self):
        self.environment.setup()

    def run(self):
        pass
