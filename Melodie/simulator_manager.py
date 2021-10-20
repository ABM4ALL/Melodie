"""
This data stores the run function for model running, storing global variables and other services.
"""
import abc
import os.path
import time
from multiprocessing import Pool
from typing import ClassVar, TYPE_CHECKING, Optional, List, Dict, Tuple
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

        self.scenario_class: Optional[ClassVar['Scenario']] = None

        self.scenarios_dataframe: Optional[pd.DataFrame] = None
        self.agent_params_dataframe: Optional[pd.DataFrame] = None
        self._static_tables: Optional[Dict[str, pd.DataFrame]] = {}

        self.scenarios: Optional[List['Scenario']] = None

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
        assert self.scenarios_dataframe is not None
        assert self.scenario_class is not None
        table = self.scenarios_dataframe
        cols = [col for col in table.columns]
        scenarios: List[Scenario] = []
        for i in range(table.shape[0]):
            scenario = self.scenario_class()
            scenario.manager = self
            for col_name in cols:
                assert col_name in scenario.__dict__.keys()
                scenario.__dict__[col_name] = table.loc[i, col_name]
            scenarios.append(scenario)
        assert len(scenarios) != 0
        return scenarios

    def generate_agent_params_dataframe(self) -> pd.DataFrame:
        # generate the parameter dataframe for agents.g
        # 这个函数必须写，分两种情况
        # (A) 最简单的，直接让agent_params_dataframe等于某张static_table。
        # (B) 自己写函数，基于1.2和2.1生成agent_params_dataframe
        #     (B1) 最简单的情况，是直接用类似于现在的add方法，基于1.2生成agent_params_dataframe。
        #     (B2) 复杂一点，比如参数之间有依赖关系、用到1.2和2.1，让用户自己写函数生成agent_params_dataframe。
        # 补充：有些参数无关启动模型，属于中间结果（比如每期的收益），此处初始化为0。
        pass

    def pre_run(self):
        """
        `pre_run` means this function should be executed before `run` or `run_parallel`, to initialize the scenarios
        and agent parameters.

        This method also clears database.
        :return:
        """
        self.register_static_tables()
        self.scenarios_dataframe = self.create_scenarios_dataframe()
        self.scenarios = self.generate_scenarios()
        assert self.scenarios is not None
        self.agent_params_dataframe = self.generate_agent_params_dataframe()
        create_db_conn(self.config).reset()

    def run_model(self, model_class, config, scenario, agent_class, environment_class,
                  data_collector_class, run_id):
        """
        
        :return: 
        """
        logger.info(f'Running {run_id + 1} times in scenario {scenario.id}.')
        t0 = time.time()
        model = model_class(config,
                            scenario,
                            agent_class,
                            environment_class,
                            data_collector_class,
                            run_id_in_scenario=run_id)

        model.setup()
        assert model.environment_class is not None
        model._setup()
        t1 = time.time()
        model.run()
        t2 = time.time()

        # if analyzer_class is not None:
        # analyzer_class().run()
        t3 = time.time()

        model_setup_time = t1 - t0
        model_run_time = t2 - t1
        analyzer_run_time = t3 - t2
        if model.data_collector is not None:
            data_collect_time = model.data_collector._time_elapsed
            model_run_time -= data_collect_time
        info = (f'Running {run_id + 1} in scenario {scenario.id} completed with time elapsed(seconds):\n'
                f'    model-setup   \t {round(model_setup_time, 6)}\n'
                f'    model-run     \t {round(model_run_time, 6)}\n')
        if model.data_collector is not None:
            info += f'    data-collect  \t {round(data_collect_time, 6)}\n'
        info += f'    the analyzer  \t {round(analyzer_run_time, 6)}'
        logger.info(info)

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
        Main function for running model!
        """
        t0 = time.time()
        self.config = config
        self.scenario_class = scenario_class
        self.pre_run()

        logger.info('Loading scenarios and static tables...')
        t1 = time.time()
        for scenario_index, scenario in enumerate(self.scenarios):
            for run_id in range(scenario.number_of_run):
                self.run_model(model_class, config, scenario, agent_class, environment_class, data_collector_class,
                               run_id)

            logger.info(f'{scenario_index + 1} of {len(self.scenarios)} scenarios has completed.')

        t2 = time.time()
        logger.info(f'Melodie completed all runs, time elapsed totally {t2 - t0}s, and {t2 - t1}s for running.')

    def run_parallel(self,
                     agent_class: ClassVar['Agent'],
                     environment_class: ClassVar['Environment'],
                     config: 'Config' = None,
                     data_collector_class: ClassVar['DataCollector'] = None,
                     model_class: ClassVar['Model'] = None,
                     scenario_class: ClassVar['Scenario'] = None,
                     scenario_manager_class: ClassVar['ScenarioManager'] = None,
                     table_generator_class: ClassVar['TableGenerator'] = None,
                     analyzer_class: ClassVar['Analyzer'] = None,
                     cores: int = 2
                     ):
        """
        Parallel model running

        Sqlite itself was thread-safe. However, pandas tries to create the table if table was not exist.
        Pandas might try to create a table when other process has created it, so it might raise exception.

        :return:
        """
        t0 = time.time()
        self.config = config
        self.scenario_class = scenario_class
        self.pre_run()

        t1 = time.time()
        logger.info('Loading scenarios and static tables...')
        pool = Pool(cores)

        parameters: List[Tuple] = []
        for scenario_index, scenario in enumerate(self.scenarios):
            for run_id in range(scenario.number_of_run):
                params = (model_class, config, scenario, agent_class, environment_class, data_collector_class,
                          run_id)
                parameters.append(params)

        logger.info(f'Melodie will run totally {len(parameters)} times!.')
        logger.info('Running the first session with only one core to verify this model...')
        self.run_model(*parameters.pop())
        logger.info(f'Verification finished, now using {cores} cores for parallel computing!')
        pool.starmap(self.run_model, parameters)

        pool.close()  # 关闭进程池，不再接受新的进程
        pool.join()  #
        t2 = time.time()
        logger.info(f'Melodie completed all runs, time elapsed totally {t2 - t0}s, and {t2 - t1}s for running.')
