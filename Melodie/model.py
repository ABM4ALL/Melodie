import sys
from typing import ClassVar, Optional

from .agent import Agent
from .agent_manager import AgentManager
from .config import Config
from .datacollector import DataCollector
from .environment import Environment
from .scenariomanager import Scenario
from .table_generator import TableGenerator
from .db import create_db_conn


class Model:
    def __init__(self, config: 'Config',
                 agent_class: ClassVar[Agent],
                 environment_class: ClassVar[Environment],
                 data_collector_class: ClassVar[DataCollector] = None,
                 table_generator_class: ClassVar[TableGenerator] = None,
                 scenario: Scenario = None,
                 run_id_in_scenraio: int = 0
                 ):

        self.proj_name = config.project_name
        self.config = config
        self.agent_class = agent_class
        self.scenario = scenario
        self.environment = environment_class()
        self.agent_manager: AgentManager = None
        self.data_collector_class = data_collector_class
        self.table_generator_class = table_generator_class
        self.data_collector: Optional[DataCollector] = None
        self.table_generator: Optional[TableGenerator] = None
        self.run_id_in_scenraio = run_id_in_scenraio

    def setup_agent_manager(self):
        """
        Setup the agent manager. The steps included:
        1. Create the self.agent_manager;
        2. Set parameters of all agents generated in current scenario;

        :return:
        """
        from .run import get_config
        self.agent_manager = AgentManager(self.agent_class, self.scenario.agent_num)
        if get_config().with_db == False:
            return
            # Read agent parameters from database
        db_conn = create_db_conn()
        agent_para_data_frame = db_conn.read_dataframe(db_conn.AGENT_PARAM_TABLE)
        # Create agent manager

        reserved_param_names = ['id']
        param_names = reserved_param_names + [param for param in agent_para_data_frame.columns if param not in
                                              {'scenario_id', 'id'}]

        # Assign parameters to properties for each agent.
        for i, agent in enumerate(self.agent_manager.agents):
            params = {}
            for agent_param_name in param_names:
                # .item() was applied to convert pandas/numpy data into python-builtin types.
                params[agent_param_name] = agent_para_data_frame.loc[i, agent_param_name].item()

            agent.set_params(params)

        return self.agent_manager

    def setup_environment(self):
        self.environment.setup()

    def setup_data_collector(self, data_collector_class):
        if callable(data_collector_class) and issubclass(data_collector_class, DataCollector):
            data_collector = data_collector_class()
            data_collector.setup()
        elif data_collector_class is None:
            data_collector = None
        else:
            raise TypeError(data_collector_class)

        self.data_collector = data_collector

    def setup_table_generator(self, table_generator_class):
        """
        TODO table generator should be set up before model creates.
        :param table_generator_class:
        :return:
        """
        # raise DeprecationWarning('table generator should be set up before model creates.')
        if table_generator_class is not None:
            self.table_generator: TableGenerator = table_generator_class(self.scenario)
            self.table_generator.setup()
            # self.table_generator.run()
        # else:

    def get_agent_param(self):
        if self.table_generator is not None:
            self.table_generator.run()
        else:
            table = ''

    def _setup(self):

        self.setup_data_collector(self.data_collector_class)
        self.setup_table_generator(self.table_generator_class)
        self.get_agent_param()
        self.setup_environment()
        self.setup_agent_manager()

    def step(self):
        pass

    def run(self):
        for i in range(self.scenario.periods):
            self.step()
            if self.data_collector is not None:
                self.data_collector.collect(i)
        if self.data_collector is not None and self.config.with_db:
            self.data_collector.save()
