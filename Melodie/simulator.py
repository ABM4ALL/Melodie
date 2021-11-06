"""
This data stores the run function for model running, storing global variables and other services.
"""
import abc
import os.path
import threading
import time
from multiprocessing import Pool
from typing import ClassVar, TYPE_CHECKING, Optional, List, Dict, Tuple
import logging

import pandas as pd

import Melodie.visualization
from . import DB
from .agent import Agent

from .agent_list import AgentList

from .table_generator import TableGenerator

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    )
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .environment import Environment
    from .model import Model
    from .scenario_manager import ScenarioManager, Scenario
    from .data_collector import DataCollector
    from .config import Config
    from .visualization import NetworkVisualizer
else:
    from .scenario_manager import ScenarioManager, Scenario
    from .config import Config
    from .db import create_db_conn


class Simulator(metaclass=abc.ABCMeta):
    def __init__(self):
        self.config: Optional[Config] = None
        self.server_thread: threading.Thread = None
        self.scenario_class: Optional[ClassVar['Scenario']] = None
        self.scenarios_dataframe: Optional[pd.DataFrame] = None
        self.agent_params_dataframe: Optional[pd.DataFrame] = None
        self.registered_tables: Optional[Dict[str, pd.DataFrame]] = {}
        self.scenarios: Optional[List['Scenario']] = None

    @abc.abstractmethod
    def register_static_tables(self):
        """
        This method must be overriden.

        The scenarios/agents parameter tables can also be registered in this method.

        :return:
        """
        # 必须有，因为至少要注册scenarios这张表
        pass

    @abc.abstractmethod
    def register_generated_tables(self):
        # 新加的函数，不一定需要写。
        # 但是，考虑到agent_params大概率跟scenarios有依赖关系，所以这个函数也大概率要写。
        pass

    def register_table(self, table_name: str, file_name: str):
        # register_table(self, table_name: str, file_name: str, data_type: dict, storage_type: Optional[Union["RAM", "ROM"]]="RAM"):
        """
        Register static table, saving it to `self.registered_tables`.
        The static table will be copied into database.

        If the scenarios/agents parameter tables can also be registered by this method.

        :param table_name: The table name, and same the name of table in database.
        :param file_name: The excel filename.
            if ends with `.xls` or `.xlsx`, This file will be searched at Config.excel_folder
            else if ends with `.csv`, This file will be searched at Config.csv_folder
        :return:
        """
        _, ext = os.path.splitext(file_name)
        table = Optional[pd.DataFrame]
        assert table_name.isidentifier(), f"table_name `{table_name}` was not an identifier!"
        if ext in {'.xls', '.xlsx'}:
            file_path_abs = os.path.join(self.config.excel_source_folder, file_name)
            table = pd.read_excel(file_path_abs)
        else:
            raise NotImplemented(file_name)

        # 修改后的步骤：
        # 1. 把table按照data_type存入数据库 --> 每张被注册的表必须存到数据库里，因为跑完Simulator再跑Analyzer的时候可能会用。
        # 2. 根据storage_type赋给self.registered_tables
        #    if storage_type == "RAM":
        #        self.registered_tables[table_name] = table.astype(data_type)
        #    elif storage_type == "ROM":
        #        self.registered_tables[table_name] = None
        #    else: pass

        self.registered_tables[table_name] = table

    def get_registered_table(self, table_name) -> pd.DataFrame:
        """
        Get a static table.
        :param table_name:
        :return:
        """

        # if registered_tables[table_name] != None:
        #     return self.registered_tables[table_name]
        # elif registered_tables[table_name] == None:
        #     return db.read_dataframe(table_name)

        return self.registered_tables[table_name]

    @abc.abstractmethod
    def generate_scenarios(self) -> List['Scenario']:
        """
        Generate scenario objects by the parameter from static tables or scenarios_dataframe.
        :return:
        """
        self.scenarios_dataframe = self.get_registered_table('scenarios')
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

    @abc.abstractmethod
    def generate_agent_params_dataframe(self) -> pd.DataFrame:
        # 修改后被register_generated_tables替代了。
        pass

    def pre_run(self):
        """
        `pre_run` means this function should be executed before `run` or `run_parallel`, to initialize the scenarios
        and agent parameters.

        This method also clears database.
        :return:
        """
        self.register_static_tables()
        self.register_generated_tables()
        self.scenarios = self.generate_scenarios()
        assert self.scenarios is not None
        self.agent_params_dataframe = self.generate_agent_params_dataframe()
        print(self.agent_params_dataframe)
        create_db_conn(self.config).reset()

    def run_model(self, config, scenario, model_class: ClassVar['Model'], agent_class, environment_class,
                  data_collector_class, run_id, visualizer=None):
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
                            run_id_in_scenario=run_id,
                            visualizer=visualizer)

        model.setup()
        model._setup()
        t1 = time.time()
        model.run()
        t2 = time.time()

        model_setup_time = t1 - t0
        model_run_time = t2 - t1
        data_collect_time = model.data_collector._time_elapsed
        model_run_time -= data_collect_time
        info = (f'Running {run_id + 1} in scenario {scenario.id} completed with time elapsed(seconds):\n'
                f'    model-setup   \t {round(model_setup_time, 6)}\n'
                f'    model-run     \t {round(model_run_time, 6)}\n'
                f'    data-collect  \t {round(data_collect_time, 6)}\n')
        logger.info(info)

    def run(self,
            config: 'Config',
            scenario_class: ClassVar['Scenario'],
            model_class: ClassVar['Model'],
            agent_class: ClassVar['Agent'],
            environment_class: ClassVar['Environment'],
            data_collector_class: ClassVar['DataCollector'],
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
                self.run_model(config, scenario, model_class, agent_class, environment_class, data_collector_class,
                               run_id)

            logger.info(f'{scenario_index + 1} of {len(self.scenarios)} scenarios has completed.')

        t2 = time.time()
        logger.info(f'Melodie completed all runs, time elapsed totally {t2 - t0}s, and {t2 - t1}s for running.')

    def run_visual(self,
                   config: 'Config',
                   scenario_class: ClassVar['Scenario'],
                   model_class: ClassVar['Model'],
                   agent_class: ClassVar['Agent'],
                   environment_class: ClassVar['Environment'],
                   data_collector_class: ClassVar['DataCollector'],
                   visualizer_class: ClassVar['Visualizer'],
                   ):
        """
        Main function for running model!
        """
        t0 = time.time()
        self.config = config
        self.scenario_class = scenario_class
        self.pre_run()
        visualizer: NetworkVisualizer = visualizer_class()

        logger.info('Loading scenarios and static tables...')
        t1 = time.time()
        while True:
            try:
                scenario = self.scenarios[0]
                self.run_model(config, scenario, model_class, agent_class, environment_class, data_collector_class,
                               run_id=0, visualizer=visualizer)
            except Melodie.visualization.MelodieModelReset as e:
                ws = e.ws
                # reset the visualizer
                visualizer.reset()
                # visualizer
                import traceback
                traceback.print_exc()

        t2 = time.time()
        logger.info(f'Melodie completed all runs, time elapsed totally {t2 - t0}s, and {t2 - t1}s for running.')

    def run_parallel(self,
                     config: 'Config',
                     scenario_class: ClassVar['Scenario'],
                     model_class: ClassVar['Model'],
                     agent_class: ClassVar['Agent'],
                     environment_class: ClassVar['Environment'],
                     data_collector_class: ClassVar['DataCollector'],
                     cores: int = 2
                     ):
        """
        Parallel model running

        Melodie does not start subprocesses directly. For the first shot, which means running one of the runs out of
        one scenario, it will be run by the main-thread to verify the model and initialize the database.
        After the first shot, subprocesses will be created as many as the value of parameter `cores`.

        :param cores
          determines how many subprocesses will be created after the first shot.

          - It is suggested that this parameter should be NO MORE THAN the 'physical cores' of your computer.
          - Beside 'cores', You may found that your cpu has one more metric: threads, which means your CPU supports
            hyper-threading. If so, use 'physical cores', not 'threads' as the upper limit.
          - For example, an Intel® I5-8250U has 4 physical cores and 8 threads. If you use a computer equipped with
            this CPU, this parameter cannot be larger than 4.
          - In short, hyper-threading only improves performance in io intensive programs. As Melodie was computation
            intensive, if there are more subprocess than physical cores, subprocesses will fight for CPU, costing
            a lot of extra time.

        Sqlite itself was thread-safe for writing. However, pandas tries to create the table if table was not exist, which
        might trigger conflict condition.

        For example:
            p1, p2 stands for process 1 and 2 request writing to a table `test`;
            db stands for database;
            1. p1 --> db <found no table named 'test'>
            2. p2 --> db <found no table named 'test'>
            3. p1 --> db <request the db to create a table 'test'>
            4. p2 --> db <request the db to create a table 'test'>
            5. db --> p1 <created table named 'test'>
            6. db --> p2 <table 'test' already exists!> ERROR!
        For multiple-cores, if running modelthis might happen very frequently. To avoid this, Melodie makes the first
        shot, which means running one of the runs out of one scenario, by main-process. If first shot completes, the
        subprocesses will be launched.

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
