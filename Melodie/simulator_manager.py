"""
This data stores the run function for model running, storing global variables and other services.
"""
import abc
import os.path
import time
from typing import ClassVar, TYPE_CHECKING, Optional, List, Dict
import logging

import pandas as pd

from . import DB
from .agent import Agent
from .agent_manager import AgentManager
from .table_generator import TableGenerator

# 拆分为几个run：simulator, analyzer, calibrator

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    )
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .environment import Environment
    from .model import Model
    from .scenario_manager import ScenarioManager, Scenario
    from .datacollector import DataCollector
    from .config import Config
else:
    from .scenario_manager import ScenarioManager
    from .config import Config
    from .db import create_db_conn


class Simulator:
    def __init__(self):
        self.config: Optional[Config] = None
        self.model: Optional[Model] = None
        self._static_tables: Optional[Dict[str, pd.DataFrame]] = None

    def get_static_table(self, table_name) -> pd.DataFrame:
        """
        Get a static table.
        :param table_name:
        :return:
        """
        return self._static_tables[table_name]

    def register_static_table(self, table_name: str, file_name: str):
        """
        Register static table, saving it to `self._static_tables`.
        The static table will be copied into database.

        If the scenarios/agents parameter tables can also be registered by this method.

        :param table_name: The table name, and same the name of table in database.
        :param file_name: The excel filename.
            if endswith `.xls` or `.xlsx`, This file will be searched at Config.excel_folder
            else if endswith `.csv`, This file will be searched at Config.csv_folder
        :return:
        """
        _, ext = os.path.splitext(file_name)
        table = Optional[pd.DataFrame]
        assert table_name.isidentifier(), f"table_name `{table_name}` was not an identifier!"
        if ext in {'.xls', '.xlsx'}:

            file_path_abs = os.path.join(self.config.excel_source_folder, file_name)
            table = pd.read_excel(file_path_abs)
        elif ext in {'.csv'}:

            file_path_abs = os.path.join(self.config.csv_source_folder, file_name)
            table = pd.read_csv(file_path_abs)
        else:
            raise NotImplemented(file_name)
        self._static_tables[table_name] = table

    @abc.abstractmethod
    def register_static_tables(self):
        """
        This method must be overriden.

        The scenarios/agents parameter tables can also be registered in this method.

        :return:
        """
        # 这个函数必须写：注册每一张excel_source文件夹里的表，包括：变量名、excel表名、列名、列数据类型。
        # 1. 注册Scenarios.xlsx
        # 2. 注册其他的static_table
        #  - assert以上写对了 --> 虽然麻烦，但可以帮助用户少犯错。
        # 把这些表导入sqlite数据库。

    def create_scenarios_dataframe(self) -> pd.DataFrame:
        """
        Generate dataframe for scenario parameters

        If scenarios parameter table has been registered at `self.register_static_tables` method with
        table name `scenarios`,
        you could simply return a dataframe by `self.get_static_table("scenarios")`
        :return:
        """
        # 对每个Scenario的实例，初始化三部分：
        # 1. attributes --> Scenarios.xlsx里的一行
        # 2. agent_params_table --> 用于model.setup_agent_list
        # 3. Scenarios以外的static_table
        # 之后，在agent和env里面，可以直接用scenario.name访问这些attributes和表。
        pass

    def generate_scenarios(self) -> List['Scenario']:
        """
        Generate scenario objects by the parameter from static tables or scenarios_dataframe.

        :return:
        """
        # 对每个Scenario的实例，初始化三部分：
        # 1. attributes --> Scenarios.xlsx里的一行
        # 2. agent_params_table --> 用于model.setup_agent_list
        # 3. Scenarios以外的static_table
        # 之后，在agent和env里面，可以直接用scenario.name访问这些attributes和表。
        pass

    def generate_agent_params_dataframe(self) -> pd.DataFrame:
        # generate the parameter dataframe for agents.g
        # 这个函数必须写，分两种情况
        # (A) 最简单的，直接让agent_params_dataframe等于某张static_table。
        # (B) 自己写函数，基于1.2和2.1生成agent_params_dataframe
        #     (B1) 最简单的情况，是直接用类似于现在的add方法，基于1.2生成agent_params_dataframe。
        #     (B2) 复杂一点，比如参数之间有依赖关系、用到1.2和2.1，让用户自己写函数生成agent_params_dataframe。
        # 补充：有些参数无关启动模型，属于中间结果（比如每期的收益），此处初始化为0。
        pass

    # def create_db_conn(self) -> 'DB':
    #     """
    #     Create database connection.
    #     :return:
    #     """
    #     return create_db_conn(self.config)

    def run(self,
            agent_class: ClassVar['Agent'],
            environment_class: ClassVar['Environment'],
            config: 'Config' = None,
            data_collector_class: ClassVar['DataCollector'] = None,
            model_class: ClassVar['Model'] = None,
            scenario_class: ClassVar['Scenario'] = None,
            scenario_manager_class: ClassVar['ScenarioManager'] = None,
            table_generator_class: ClassVar['TableGenerator'] = None,
            analyzer_class: ClassVar['Analyzer'] = None
            ):
        """
        Main Model for running model!
        If
        """
        from .model import Model

        # global self.model, _config, _current_scenario
        # if config is None:
        #     config = Config('Untitled')
        #     _config = config
        # else:
        #     _config = config
        # if _config.with_db:
        self.config = config
        create_db_conn(self.config).reset()

        if model_class is None:
            model_class = Model

        logger.info('Loading scenarios and static tables...')
        if scenario_manager_class is None:
            scenario_manager = ScenarioManager(config, scenario_class)
        else:
            scenario_manager: 'ScenarioManager' = scenario_manager_class(config, scenario_class)

        if config.with_db:
            scenarios = scenario_manager.load_scenarios()
        else:
            scenarios = scenario_manager.gen_scenarios()
        for scenario_index, scenario in enumerate(scenarios):
            # _current_scenario = scenario
            for run_id in range(scenario.number_of_run):
                logger.info(f'Running {run_id + 1} times in scenario {scenario.id}.')
                t0 = time.time()
                self.model = model_class(config,
                                         scenario,
                                         agent_class,
                                         environment_class,
                                         data_collector_class,
                                         table_generator_class=table_generator_class,
                                         run_id_in_scenario=run_id)

                self.model.setup()
                assert self.model.environment_class is not None
                self.model._setup()
                t1 = time.time()
                self.model.run()
                t2 = time.time()

                # if analyzer_class is not None:
                # analyzer_class().run()
                t3 = time.time()

                model_setup_time = t1 - t0
                model_run_time = t2 - t1
                analyzer_run_time = t3 - t2
                if self.model.data_collector is not None:
                    data_collect_time = self.model.data_collector._time_elapsed
                    model_run_time -= data_collect_time
                info = (f'Running {run_id + 1} in scenario {scenario.id} completed with time elapsed(seconds):\n'
                        f'    model-setup   \t {round(model_setup_time, 6)}\n'
                        f'    model-run     \t {round(model_run_time, 6)}\n')
                if self.model.data_collector is not None:
                    info += f'    data-collect  \t {round(data_collect_time, 6)}\n'
                info += f'    the analyzer  \t {round(analyzer_run_time, 6)}'
                logger.info(info)

            logger.info(f'{scenario_index + 1} of {len(scenarios)} scenarios has completed.')

    def run_parallel(self):
        """
        Parallel model running
        :return:
        """
        pass
