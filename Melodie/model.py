import sys
from typing import ClassVar, Optional, Union

import pandas as pd

from . import DB
from .agent import Agent
from .agent_list import AgentList
from .config import Config
from .data_collector import DataCollector
from .environment import Environment
from .scenario_manager import Scenario
from .table_generator import TableGenerator
from .db import create_db_conn


class Model:
    def __init__(self,
                 config: 'Config',
                 scenario: 'Scenario',
                 agent_class: ClassVar[Agent] = None,
                 environment_class: ClassVar[Environment] = None,
                 data_collector_class: ClassVar[DataCollector] = None,
                 run_id_in_scenario: int = 0,
                 visualizer=None
                 ):
        self.scenario = scenario
        self.project_name = config.project_name
        self.config = config
        self.agent_class = agent_class
        self.environment_class = environment_class
        self.data_collector_class = data_collector_class
        self.environment: Environment
        self.data_collector: Optional[DataCollector] = None
        self.table_generator: Optional[TableGenerator] = None
        self.run_id_in_scenario = run_id_in_scenario

        self.network = None
        self.visualizer = visualizer

    def setup(self):
        pass

    def current_scenario(self) -> 'Scenario':
        assert self.scenario != None
        return self.scenario

    def create_db_conn(self) -> 'DB':
        return create_db_conn(self.config)

    def get_agent_param(self):
        # 之后就没用了，统一用get_registered_table
        if self.table_generator is not None:
            self.table_generator.run()
        else:
            table = ''

    def new_setup_agent_list(self, agent_para_data_frame):
        # 新增函数，替代下面的setup_agent_list，方便用户自己初始化模型中的agent_list

        """
        Setup the agent manager. The steps included:
        1. Create the self.agent_list;
        2. Set parameters of all agents generated in current scenario;

        :return:
        """
        scenario = self.scenario
        self.agent_list = AgentList(self.agent_class, scenario.agent_num, self)

        # Create agent manager

        reserved_param_names = ['id']
        param_names = reserved_param_names + [param for param in agent_para_data_frame.columns if param not in
                                              {'scenario_id', 'id'}]

        # Assign parameters to properties for each agent.
        for i, agent in enumerate(self.agent_list.agents):
            params = {}
            for agent_param_name in param_names:
                # .item() was applied to convert pandas/numpy data into python-builtin types.
                params[agent_param_name] = agent_para_data_frame.loc[i, agent_param_name].item()

            agent.set_params(params)

        return self.agent_list

    def setup_environment(self):
        self.environment = self.environment_class()
        self.environment.model = self
        self.environment.setup()

    def setup_data_collector(self):
        data_collector_class = self.data_collector_class
        if callable(data_collector_class) and issubclass(data_collector_class, DataCollector):
            data_collector = data_collector_class(self)
            data_collector.setup()
        else:
            raise TypeError(data_collector_class)
        self.data_collector = data_collector

    def _setup(self):
        self.get_agent_param()
        self.setup_environment()
        self.setup_data_collector()

    def create_agent_container(self, agent_class: ClassVar['Agent'], length: int,
                               params_df: pd.DataFrame = None,
                               container_type: str = "list") -> Union[AgentList]:
        agent_container_class: Union[ClassVar[AgentList], None] = None
        if container_type == "list":
            agent_container_class = AgentList
        else:
            raise NotImplementedError

        container = agent_container_class(agent_class, length, model=self)
        if params_df is not None:
            container.set_properties(params_df)
        return container

    def run(self):
        pass
