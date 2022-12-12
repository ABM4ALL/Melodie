"""
This data stores the run function for model running, storing global variables and other services.
"""
import abc
import logging
import os
import threading
import time
from multiprocessing import Pool
from typing import Optional, List, Tuple, Type

import numpy as np
import pandas as pd

from MelodieInfra import create_db_conn, get_sqlite_filename, DBConn, Config, MelodieExceptions, show_prettified_warning

from .global_configs import MelodieGlobalConfig
from .data_loader import DataLoader
from .model import Model
from .scenario_manager import Scenario
from .visualizer import BaseVisualizer, MelodieModelReset

logger = logging.getLogger(__name__)


class BaseModellingManager(abc.ABC):
    """
    Base class of Simulator/Trainer/Calibrator.
    """

    def __init__(
            self,
            config: Config,
            scenario_cls: Type["Scenario"],
            model_cls: Type["Model"],
            data_loader_cls: Type[DataLoader] = None,
    ):
        self.config: Optional[Config] = config
        self.scenario_cls = scenario_cls
        self.model_cls = model_cls

        self.scenarios: Optional[List["Scenario"]] = None
        self.df_loader_cls: Optional[Type[DataLoader]] = data_loader_cls
        self.data_loader: Optional[DataLoader] = None
        if data_loader_cls is not None:
            assert issubclass(data_loader_cls, DataLoader), data_loader_cls

    def get_dataframe(self, table_name) -> pd.DataFrame:
        """
        Get a static data frame from data loader.

        :param table_name:
        :return:
        """
        if self.data_loader is None:
            raise MelodieExceptions.Data.NoDataframeLoaderDefined()
        if table_name not in self.data_loader.registered_dataframes:
            raise MelodieExceptions.Data.StaticTableNotRegistered(
                table_name, list(self.data_loader.registered_dataframes.keys())
            )

        return self.data_loader.registered_dataframes[table_name]

    def get_matrix(self, matrix_name) -> np.ndarray:
        """
        Get a matrix from data loader.

        :param matrix_name:
        :return:
        """
        if self.data_loader is None:
            raise MelodieExceptions.Data.NoDataframeLoaderDefined()
        if matrix_name not in self.data_loader.registered_matrices:
            raise MelodieExceptions.Data.StaticTableNotRegistered(
                matrix_name, list(self.data_loader.registered_matrices.keys())
            )

        return self.data_loader.registered_matrices[matrix_name]

    def subworker_prerun(self):
        """
        If run as sub-worker, run this function to avoid deleting the existing tables in database.

        :return:
        """
        self.data_loader: DataLoader = self.df_loader_cls(
            self, self.config, self.scenario_cls, as_sub_worker=True
        )

        self.scenarios = self.generate_scenarios()

    def pre_run(self, clear_db=True):
        """
        `pre_run` means this function should be executed before `run`, to initialize the scenario
        parameters.

        This method also clears database.
        :return:
        """
        if clear_db:
            create_db_conn(self.config).clear_database()
        if self.df_loader_cls is not None:
            self.data_loader: DataLoader = self.df_loader_cls(
                self, self.config, self.scenario_cls
            )

        self.scenarios = self.generate_scenarios()
        if self.scenarios is None or len(self.scenarios) == 0:
            MelodieExceptions.Scenario.NoValidScenarioGenerated(self.scenarios)

    @abc.abstractmethod
    def generate_scenarios(self):
        pass


class Simulator(BaseModellingManager):
    def __init__(
            self,
            config: Config,
            scenario_cls: "Type[Scenario]",
            model_cls: "Type[Model]",
            data_loader_cls: "Type[DataLoader]" = None,
            visualizer_cls: "type[BaseVisualizer]" = None,
    ):
        super(Simulator, self).__init__(
            config=config,
            scenario_cls=scenario_cls,
            model_cls=model_cls,
            data_loader_cls=data_loader_cls,
        )
        self.server_thread: Optional[threading.Thread] = None
        self.visualizer_cls = visualizer_cls
        self.visualizer = None

    def _init_visualizer(self):
        self.visualizer: Optional[BaseVisualizer] = (
            None if self.visualizer_cls is None else self.visualizer_cls(self.config, self)
        )

    def generate_scenarios(self) -> List["Scenario"]:
        """
        Generate scenarios from the dataframe_loader

        :return:
        """
        if self.data_loader is None:
            raise MelodieExceptions.Data.NoDataframeLoaderDefined()
        return self.data_loader.generate_scenarios("simulator")

    def run_model(
            self, config, scenario, id_run, model_class: Type["Model"], visualizer=None
    ):
        """
        Run a model once.

        :return:
        """
        logger.info(
            f"Simulation started - id_scenario = {scenario.id}, id_run = {id_run}"
        )
        t0 = time.time()

        model: Model = model_class(
            config, scenario, run_id_in_scenario=id_run, visualizer=visualizer
        )
        if visualizer is not None:
            visualizer.set_model(model)
            if not self.visualizer.params_manager._initialized:
                self.visualizer.params_manager.write_obj_attrs_to_params_list(scenario,
                                                                              self.visualizer.params_manager.params)
                self.visualizer.params_manager._initialized = True
            else:
                self.visualizer.params_manager.modify_scenario(scenario)
            # with open('test.json', 'w') as f:
            #     json.dump({
            #         'model': self.visualizer.params_manager.to_json(),
            #         'params-values': self.visualizer.params_manager.to_value_json()
            #     }, f, indent=4)
            # with open('123.json') as f:
            #     self.visualizer.params_manager.from_json(json.load(f))
            # with open('out.json', 'w') as f:
            #     json.dump({
            #         'model': self.visualizer.params_manager.to_json(),
            #         'params-values': self.visualizer.params_manager.to_value_json()
            #     }, f, indent=4)
            # self.visualizer.params_manager.modify_scenario(scenario)
            print('aaa', self.visualizer.params_manager.to_value_json()[0])
            visualizer.start()
        else:
            model._setup()

        t1 = time.time()
        model.run()
        if visualizer is not None:
            model.visualizer.finish()
        t2 = time.time()

        model_setup_time = t1 - t0
        model_run_time = t2 - t1
        if model.data_collector is not None:
            data_collect_time = model.data_collector.time_elapsed()
        else:
            data_collect_time = 0.0
        model_run_time -= data_collect_time
        info = (
            f"Simulation completed - id_scenario = {scenario.id}, id_run = {id_run}\n"
            f"    model-setup   \t {MelodieGlobalConfig.Logger.round_elapsed_time(model_setup_time)}s\n"
            f"    model-run     \t {MelodieGlobalConfig.Logger.round_elapsed_time(model_run_time)}s\n"
            f"    data-collect  \t {MelodieGlobalConfig.Logger.round_elapsed_time(data_collect_time)}s\n"
        )
        logger.info(info)

    def setup(self):
        """
        Setup method of simulator, usually need not to inherit.

        :return: None
        """
        pass

    def run(self):
        """
        Main function for running model.

        :return: None
        """
        t0 = time.time()
        BaseVisualizer.enabled = False
        self.setup()
        if self.visualizer_cls is not None:
            show_prettified_warning(
                "You are using `Simulator.run()` method to run model, but you have also defined visualizer.\n"
                "If you would like to visualize this model, please use `Simulator.run_visual()` "
                "instead of `Simulator.run()` "
            )

        self.pre_run()
        t1 = time.time()
        for scenario_index, scenario in enumerate(self.scenarios):
            for id_run in range(scenario.run_num):
                self.run_model(
                    self.config, scenario, id_run, self.model_cls, visualizer=None
                )

        t2 = time.time()
        logger.info(
            f"Simulator completed, time elapsed {MelodieGlobalConfig.Logger.round_elapsed_time(t2 - t0)}s."
        )

    def run_visual(self):
        """
        Main function for running model with studio.

        :return: None
        """
        t0 = time.time()
        self._init_visualizer()
        self.setup()

        self.pre_run()
        if self.visualizer is not None:
            self.visualizer.setup()

        t1 = time.time()
        logger.info(f"Simulator start up cost: {t1 - t0}s")
        while True:
            logger.info(
                f"Visualizer interactive paramerters for this scenario are: {self.visualizer.scenario_param}"
            )
            # create_db_conn(self.config).clear_database()
            # create_db_conn()
            fn = get_sqlite_filename(self.config)
            if os.path.exists(fn):
                os.remove(fn)
            self.data_loader = None
            self.scenarios = None
            DBConn.table_dtypes = {}
            self.pre_run()
            scenario = self.scenarios[0].copy()
            scenario.manager = self

            # for k, v in self.visualizer.scenario_param.items():
            #     scenario.__setattr__(k, v)
            logger.info(f"Scenario parameters: {scenario.to_dict()}")
            try:
                self.visualizer.current_scenario = scenario  # set studio scenario.
                self.run_model(
                    self.config, scenario, 0, self.model_cls, visualizer=self.visualizer
                )
            except MelodieModelReset:

                self.visualizer.reset()
                logger.info("Model reset.")

    def run_parallel(self, cores: int = 2):
        """
        Parallel model running

        Melodie does not start subprocesses directly. For the first shot, which means running one of the runs out of
        one scenario, it will be run by the main-thread to verify the model and initialize the database.
        After the first shot, subprocesses will be created as many as the value of parameter `cores`.

        :param cores:
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
        shot, which means running one of the runs out of one scenario, by main-process. Only when first shot completes
        will the subprocesses be launched.


        :return: None
        """
        t0 = time.time()
        self.pre_run()

        t1 = time.time()
        pool = Pool(cores)

        parameters: List[Tuple] = []
        for scenario_index, scenario in enumerate(self.scenarios):
            for id_run in range(scenario.run_num):
                params = (
                    self.config,
                    scenario,
                    id_run,
                    self.model_cls,
                )
                parameters.append(params)

        logger.info(f"Melodie will run totally {len(parameters)} times!.")
        logger.info(
            "Running the first session with only one core to verify this model..."
        )
        self.run_model(*parameters.pop())
        logger.info(
            f"Verification finished, now using {cores} cores for parallel computing!"
        )
        pool.starmap(self.run_model, parameters)

        pool.close()
        pool.join()
        t2 = time.time()
        logger.info(
            f"Melodie completed all runs, time elapsed totally {t2 - t0}s, and {t2 - t1}s for running."
        )
