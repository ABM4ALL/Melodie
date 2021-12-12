"""
This data stores the run function for model running, storing global variables and other services.
"""
import abc
import contextlib
import os.path
import threading
import time
from multiprocessing import Pool
from typing import ClassVar, TYPE_CHECKING, Optional, List, Dict, Tuple, Callable, Union
import logging

import pandas as pd

import Melodie.visualization
from . import DB
from .agent import Agent

from .agent_list import AgentList

from .table_generator import TableGenerator
from .basic.exceptions import MelodieExceptions

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    )
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .environment import Environment
    from .model import Model
    from .scenario_manager import Scenario
    from .data_collector import DataCollector
    from .config import Config
    from .visualization import Visualizer
else:
    from .scenario_manager import Scenario
    from .config import Config
    from .db import create_db_conn


class Simulator(metaclass=abc.ABCMeta):
    def __init__(self):
        self.config: Optional[Config] = None
        self.server_thread: threading.Thread = None
        self.scenario_class: Optional[ClassVar['Scenario']] = None
        self.scenarios_dataframe: Optional[pd.DataFrame] = None
        self.agent_params_dataframe: Optional[pd.DataFrame] = None
        self.registered_dataframes: Optional[Dict[str, pd.DataFrame]] = {}
        self.scenarios: Optional[List['Scenario']] = None

    @abc.abstractmethod
    def register_scenario_dataframe(self) -> None:
        """
        This method must be overriden.
        The "scenarios" table will be registered in this method.
        """
        pass

    def register_static_dataframes(self) -> None:
        """
        The "agent_params" table can be registered in this method.
        """
        pass

    def register_generated_dataframes(self) -> None:
        """
        The "agent_params" table can be registered in this method.
        """
        pass

    def register_dataframe(self, table_name: str, data_frame: pd.DataFrame, data_types: dict = None) -> None:
        """

        :param table_name:
        :param data_frame:
        :param data_types:
        :return:
        """
        if data_types is None:
            data_types = {}
        DB.register_dtypes(table_name, data_types)
        create_db_conn(self.config).write_dataframe(table_name, data_frame, data_types=data_types,
                                                    if_exists="replace")
        self.registered_dataframes[table_name] = create_db_conn(self.config).read_dataframe(table_name)

    def load_dataframe(self, table_name: str, file_name: str, data_types: dict) -> None:

        """
        Register static table, saving it to `self.registered_dataframes`.
        The static table will be copied into database.

        If the scenarios/agents parameter tables can also be registered by this method.

        :param table_name: The table name, and same the name of table in database.
        :param file_name: The excel filename.
            if ends with `.xls` or `.xlsx`, This file will be searched at Config.excel_folder
        :return:
        """
        _, ext = os.path.splitext(file_name)
        table: Optional[pd.DataFrame]
        assert table_name.isidentifier(), f"table_name `{table_name}` was not an identifier!"
        if ext in {'.xls', '.xlsx'}:
            file_path_abs = os.path.join(self.config.excel_source_folder, file_name)
            table = pd.read_excel(file_path_abs)
        else:
            raise NotImplemented(file_name)

        # 注册步骤：
        # 1. 把dataframe按照data_type存入数据库，因为跑完Simulator再跑Analyzer的时候可能会用。
        # 1.1 data_type作为DB的类属性，注册进DB
        DB.register_dtypes(table_name, data_types)
        # 1.2 无需指定data_type即可按照data_type来存储table_name
        create_db_conn(self.config).write_dataframe(table_name, table, data_types=data_types,
                                                    if_exists="replace", )  # --> 加上data_type

        # 2. 把dataframe放到registered_dataframes里。
        self.registered_dataframes[table_name] = table

    def get_registered_dataframe(self, table_name) -> pd.DataFrame:
        """
        Get a static table.
        :param table_name:
        :return:
        """

        if table_name not in self.registered_dataframes:
            raise MelodieExceptions.Data.StaticTableNotRegistered(table_name, list(self.registered_dataframes.keys()))

        return self.registered_dataframes[table_name]

    def generate_scenarios_from_dataframe(self, df_name: str) -> List['Scenario']:
        """
        Generate scenario objects by the parameter from static tables
        :return:
        """
        self.scenarios_dataframe = self.get_registered_dataframe(df_name)
        assert self.scenarios_dataframe is not None
        assert self.scenario_class is not None
        table = self.scenarios_dataframe
        cols = [col for col in table.columns]
        scenarios: List[Scenario] = []
        for i in range(table.shape[0]):
            scenario = self.scenario_class()
            scenario.manager = self
            for col_name in cols:
                assert col_name in scenario.__dict__.keys(), f"col_name: '{col_name}', scenario: {scenario}"
                scenario.__dict__[col_name] = table.loc[i, col_name]
            scenarios.append(scenario)
        assert len(scenarios) != 0
        return scenarios

    def new_table_generator(self, table_name: str, rows_in_scenario: Union[int, Callable[[Scenario], int]]):
        """
        Create a new generator
        :param table_name:
        :param rows_in_scenario:
            How many rows will be generated for a specific scenario.
            This argument should be an integer as number of rows for each scenario, or a function with a parameter typed
            `Scenario` and return an integer for how many rows to generate for this scenario .
        :return:
        """
        return TableGenerator(self, table_name, rows_in_scenario)

    def generate_scenarios(self) -> List['Scenario']:
        """
        Generate scenario objects by the parameter from static tables or scenarios_dataframe.
        :return:
        """
        return self.generate_scenarios_from_dataframe('scenarios')

    def pre_run(self):
        """
        `pre_run` means this function should be executed before `run`, to initialize the scenario
        parameters.

        This method also clears database.
        :return:
        """
        create_db_conn(self.config).clear_database()
        self.register_scenario_dataframe()
        self.register_static_dataframes()
        self.register_generated_dataframes()

        self.scenarios = self.generate_scenarios()
        assert self.scenarios is not None

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
        Main function for running model with visualizer.
        """
        t0 = time.time()
        self.config = config
        self.scenario_class = scenario_class
        self.pre_run()
        visualizer: Visualizer = visualizer_class()
        visualizer.setup()
        logger.info('Loading scenarios and static tables...')
        t1 = time.time()
        while True:
            logger.info(f"Visualizer interactive paramerters for this scenario are: {visualizer.scenario_param}")
            scenario = scenario_class()
            scenario.setup()
            scenario.periods = 99999
            for k, v in visualizer.scenario_param.items():
                scenario.__setattr__(k, v)
            logger.info(f"Scenario parameters: {scenario.toDict()}")
            try:
                visualizer.current_scenario = scenario  # set visualizer scenario.
                self.run_model(config, scenario, model_class, agent_class, environment_class, data_collector_class,
                               run_id=0, visualizer=visualizer)
            except Melodie.visualization.MelodieModelReset as e:

                visualizer.reset()

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
                params = (config, scenario, model_class, agent_class, environment_class, data_collector_class,
                          run_id)
                parameters.append(params)

        logger.info(f'Melodie will run totally {len(parameters)} times!.')
        logger.info('Running the first session with only one core to verify this model...')
        self.run_model(*parameters.pop())
        logger.info(f'Verification finished, now using {cores} cores for parallel computing!')
        pool.starmap(self.run_model, parameters)

        pool.close()  # 关闭进程池，不再接受新的进程
        pool.join()
        t2 = time.time()
        logger.info(f'Melodie completed all runs, time elapsed totally {t2 - t0}s, and {t2 - t1}s for running.')

    def run_boost(self,
                  agent_class: ClassVar['Agent'],
                  environment_class: ClassVar['Environment'],
                  config: 'Config' = None,
                  data_collector_class: ClassVar['DataCollector'] = None,
                  model_class: ClassVar['Model'] = None,
                  scenario_class: ClassVar['Scenario'] = None,
                  scenario_manager_class: ClassVar['ScenarioManager'] = None,
                  table_generator_class: ClassVar['TableGenerator'] = None,
                  analyzer_class: ClassVar['Analyzer'] = None,
                  visualizer_class: ClassVar['Visualizer'] = None,
                  boost_model_class: ClassVar['Model'] = None,
                  model_components=None
                  ):
        """
        Boost.
        :param agent_class:
        :param environment_class:
        :param config:
        :param data_collector_class:
        :param model_class:
        :param scenario_class:
        :param scenario_manager_class:
        :param table_generator_class:
        :param analyzer_class:
        :param visualizer_class:
        :param boost_model_class:
        :param model_components:
        :return:
        """
        from Melodie.boost.compiler.compiler import conv
        import importlib
        conv(agent_class, environment_class, model_class, 'out.py', model_components=model_components)
        logger.warning("Testing. compilation finished, program exits")
        # return
        compiled = importlib.import_module('out')
        model_run = compiled.__getattribute__('___model___run')
        logger.info("Preprocess compilation finished, now running pre-run procedures.")

        self.config = config
        self.scenario_class = scenario_class
        self.register_scenario_dataframe()
        self.register_static_dataframes()

        # self.scenarios_dataframe = self.create_scenarios_dataframe()
        self.scenarios = self.generate_scenarios()
        assert self.scenarios is not None
        logger.info("Pre-run procedures finished. Now simulation starts...")

        t0 = time.time()
        t1 = time.time()
        first_run_finished_at = time.time()
        first_run = True
        for scenario in self.scenarios:
            for run_id in range(scenario.number_of_run):
                if first_run:
                    logger.info("Numba is now taking control of program. "
                                "It may take a few seconds for compilation.")
                visualizer = visualizer_class()
                visualizer.setup()
                visualizer.current_scenario = scenario
                model = boost_model_class(self.config,
                                          scenario,
                                          visualizer=visualizer
                                          )
                model.setup_boost()
                model_run(model)
                if first_run:
                    logger.info("The first run has completed, and numba has finished compilaiton. "
                                "Your program will be speeded up greatly.")
                    first_run_finished_at = time.time()
                    first_run = False

                logger.info(f"Finished running <experiment {run_id}, scenario {scenario.id}>. "
                            f"time elapsed: {time.time() - t1}s")
                t1 = time.time()

        logger.info(f"totally time elapsed {time.time() - t0} s,"
                    f" {(time.time() - t0) / 100}s per run, {(time.time() - first_run_finished_at) / (100 - 1)}s per run after compilation")
