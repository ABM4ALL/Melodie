import sys
from typing import ClassVar, Optional, Union

import pandas as pd

from . import DB
from .agent import Agent
from .agent_list import AgentList, BaseAgentContainer
from .basic import MelodieExceptions
from .config import Config
from .data_collector import DataCollector
from .environment import Environment
from .scenario_manager import Scenario
from .table_generator import TableGenerator
from .db import create_db_conn
from .visualization import Visualizer


class Model:
    def __init__(self,
                 config: 'Config',
                 scenario: 'Scenario',
                 agent_class: ClassVar[Agent] = None,
                 environment_class: ClassVar[Environment] = None,
                 data_collector_class: ClassVar[DataCollector] = None,
                 run_id_in_scenario: int = 0,
                 visualizer: Visualizer = None
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
        """
        general method for setting up the model.
        :return:
        """
        pass

    def setup_boost(self):
        """
        setup method for boosting.
        :return:
        """
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

    def create_agent_container(self, agent_class: ClassVar['Agent'], initial_num: int,
                               params_df: pd.DataFrame ,
                               container_type: str = "list") -> Union[AgentList]:
        """
        Create a container for agents
        :param agent_class:
        :param initial_num: Initial number of agents
        :param params_df:
        :param container_type:
        :return:
        """
        agent_container_class: Union[ClassVar[AgentList], None] = None
        if container_type == "list":
            agent_container_class = AgentList
        else:
            raise NotImplementedError(f"Container type '{container_type}' is not valid!")

        container = agent_container_class(agent_class, initial_num, model=self)
        container.set_properties(params_df)
        container.post_setup()
        return container

    def check_agent_containers(self):
        """
        Check the agent containers in the model.
        Check list is:
        - Each agent, no matter which container it was in, should have a unique id.

        :return:
        """
        for prop_name, prop in self.__dict__.items():
            if isinstance(prop, BaseAgentContainer):
                all_ids = prop.all_agent_ids()
                if len(set(all_ids)) < len(all_ids):
                    raise MelodieExceptions.Agents.AgentIDConflict(prop_name, all_ids)

    def run(self):
        pass

    def run_boost(self):
        pass
