"""
This data stores the run function for model running, storing global variables and other services.
"""
import abc
import copy
import logging
import os
import shutil
import threading
import time
from multiprocessing import Pool
from typing import Literal, Optional, List, Tuple, Type

import pandas as pd

from MelodieInfra import (
    create_db_conn,
    get_sqlite_filename,
    DBConn,
    Config,
    MelodieExceptions,
    show_prettified_warning,
    MelodieGlobalConfig,
)
from MelodieInfra.db.db import db_conn

from .data_loader import DataLoader
from .model import Model
from .scenario_manager import Scenario
from .visualizer import BaseVisualizer, MelodieModelReset

logger = logging.getLogger(__name__)


class BaseModellingManager(abc.ABC):
    """
    Base class of ``Simulator``/``Trainer``/``Calibrator``.
    """

    def __init__(
        self,
        config: Config,
        scenario_cls: Type["Scenario"],
        model_cls: Type["Model"],
        data_loader_cls: Optional[Type[DataLoader]] = None,
    ):
        self.config: Config = config
        self.scenario_cls = scenario_cls
        self.model_cls = model_cls

        self.scenarios: Optional[List["Scenario"]] = None
        self.df_loader_cls: Optional[Type[DataLoader]] = data_loader_cls
        self.data_loader: Optional[DataLoader] = None
        if data_loader_cls is None:
            self.df_loader_cls = DataLoader
        assert issubclass(self.df_loader_cls, DataLoader), self.df_loader_cls

    def get_dataframe(self, table_name) -> "pd.DataFrame":
        """
        Get a static ``DataFrame`` from the data loader.

        :param table_name: Name of dataframe.
        :return:
        """
        if self.data_loader is None:
            raise MelodieExceptions.Data.NoDataframeLoaderDefined()
        if table_name not in self.data_loader.registered_dataframes:
            raise MelodieExceptions.Data.StaticTableNotRegistered(
                table_name, list(self.data_loader.registered_dataframes.keys())
            )

        return self.data_loader.registered_dataframes[table_name]

    def get_matrix(self, matrix_name) -> "np.ndarray":
        """
        Get a matrix from data loader.

        :param matrix_name: Name of matrix.
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
        """
        if self.df_loader_cls is not None:
            self.data_loader: DataLoader = self.df_loader_cls(
                self, self.config, self.scenario_cls, as_sub_worker=True
            )

        self.scenarios = self.generate_scenarios()

    def clear_output_tables(self):
        """
        Clear all output tables
        """
        output_path = self.config.output_tables_path()
        if os.path.exists(output_path):
            shutil.rmtree(output_path)
        os.mkdir(output_path)

    def pre_run(self, clear_output_data=True):
        """
        `pre_run` means this function should be executed before ``run``, to initialize the scenario
        parameters.

        :param clear_db: If ``True``, this method will clear database.
        :return:
        """
        assert self.config is not None, MelodieExceptions.MLD_INTL_EXC
        if clear_output_data:
            with db_conn(self.config) as conn:
                conn.clear_database()

            self.clear_output_tables()

        if self.df_loader_cls is not None:
            self.data_loader: DataLoader = self.df_loader_cls(
                self, self.config, self.scenario_cls
            )

        self.scenarios = self.generate_scenarios()

        if self.scenarios is None or len(self.scenarios) == 0:
            raise MelodieExceptions.Scenario.NoValidScenarioGenerated(self.scenarios)

    @abc.abstractmethod
    def generate_scenarios(self) -> List[Scenario]:
        """
        Abstract method for generation of scenarios.
        """
        pass

    def _write_to_table(
        self, kind: Literal["csv", "sql"], table_name: str, data: pd.DataFrame
    ):
        """
        Write a pandas dataframe to a table in output directory or database
        """
        if kind == "sql":
            create_db_conn(self.config).write_dataframe(
                table_name,
                data,
                if_exists="append",
            )
        elif kind == "csv":
            csv_file = os.path.join(
                self.config.output_tables_path(), table_name + ".csv"
            )
            if os.path.exists(csv_file):
                data.to_csv(csv_file, mode="a", header=False)
            else:
                data.to_csv(csv_file)
        else:
            raise NotImplementedError


class SimulatorMeta:
    """
    Record the current scenario, params scenario of simulator

    """

    def __init__(self):
        self._freeze = False
        self.id_simulator_scenario = 0

    def to_dict(self, public_only=False):
        if public_only:
            return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
        return copy.copy(self.__dict__)

    def __repr__(self):
        return f"<{self.to_dict()}>"

    def __setattr__(self, key, value):
        if (not hasattr(self, "_freeze")) or (not self._freeze):
            super().__setattr__(key, value)
        else:
            if key in self.__dict__:
                super().__setattr__(key, value)
            else:
                raise MelodieExceptions.General.NoAttributeError(self, key)


class Simulator(BaseModellingManager):
    """
    Simulator simulates the logics written in the model.

    """

    def __init__(
        self,
        config: Config,
        scenario_cls: "Type[Scenario]",
        model_cls: "Type[Model]",
        data_loader_cls: "Type[DataLoader]" = None,
        visualizer_cls: "type[BaseVisualizer]" = None,
    ):
        """
        :param config: Config instance for current project.
        :param scenario_cls: Scenario class for current project.
        :param model_cls: Model class in current project.
        :param data_loader_cls: DataLoader class in current project.
        :param visualizer_cls: Visualizer class in current project.
        """
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
            None
            if self.visualizer_cls is None
            else self.visualizer_cls(self.config, self)
        )

    def generate_scenarios(self) -> List["Scenario"]:
        """
        Generate scenarios from the dataframe_loader

        :return: A list of generated scenarios.
        """
        if self.data_loader is None:
            raise MelodieExceptions.Data.NoDataframeLoaderDefined()

        return self.data_loader.generate_scenarios("Simulator")

    def run_model(
        self, config, scenario, id_run, model_class: Type["Model"], visualizer=None
    ):
        """
        Run a model once.
        """
        logger.info(
            f"Simulation started - id_scenario = {scenario.id}, id_run = {id_run}"
        )
        t0 = time.time()

        scenario.id_run = id_run

        model: Model = model_class(
            config, scenario, run_id_in_scenario=id_run, visualizer=visualizer
        )
        if visualizer is not None:
            visualizer.set_model(model)
            if not self.visualizer.params_manager._initialized:
                self.visualizer.params_manager.write_obj_attrs_to_params_list(
                    scenario, self.visualizer.params_manager.params
                )
                self.visualizer.params_manager._initialized = True
            else:
                self.visualizer.params_manager.modify_scenario(scenario)
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

        assert self.scenarios is not None, MelodieExceptions.MLD_INTL_EXC
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
        Main function for running model with visualization.

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

        assert self.visualizer is not None, MelodieExceptions.MLD_INTL_EXC
        assert self.config is not None, MelodieExceptions.MLD_INTL_EXC

        while True:
            logger.info(
                f"Visualizer interactive paramerters for this scenario are: {self.visualizer.scenario_param}"
            )
            fn = get_sqlite_filename(self.config)
            if os.path.exists(fn):
                os.remove(fn)
            self.data_loader: "Optional[DataLoader]" = None
            self.scenarios = None
            DBConn.table_dtypes = {}
            self.pre_run()
            assert self.scenarios is not None, MelodieExceptions.MLD_INTL_EXC
            logger.warning(
                "When running visualizer, only the first scenario will be run."
            )
            scenario = self.scenarios[0].copy()
            scenario.manager = self

            # for k, v in self.visualizer.scenario_param.items():
            #     scenario.__setattr__(k, v)
            logger.info(f"Scenario parameters: {scenario.to_dict()}")
            try:
                # set studio scenario.
                self.visualizer.current_scenario = scenario
                self.run_model(
                    self.config, scenario, 0, self.model_cls, visualizer=self.visualizer
                )
            except MelodieModelReset:
                self.visualizer.reset()
                logger.info("Model reset.")

    def run_parallel(self, cores: int = 1):
        """
        Parallelized running through a series of scenarios.

        Melodie does not start subprocesses directly. For the first shot, which means running one of the runs out of
        one scenario, it will be run by the main-thread to verify the model and initialize the database.
        After the first shot, subprocesses will be created as many as the value of parameter `cores`.

        :param cores: How many subprocesses will be created in the parallel simulation.

          - It is suggested that this parameter should be NO MORE THAN the **physical cores** of your computer.
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

        For multiple-cores, if running model this might happen very frequently. To avoid this, Melodie makes the first
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

    def new_parallel(self, cores: int = 1):
        """
        Parallelized running through a series of scenarios.

        Melodie does not start subprocesses directly. For the first shot, which means running one of the runs out of
        one scenario, it will be run by the main-thread to verify the model and initialize the database.
        After the first shot, subprocesses will be created as many as the value of parameter `cores`.

        :param cores: How many subprocesses will be created in the parallel simulation.

          - It is suggested that this parameter should be NO MORE THAN the **physical cores** of your computer.
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

        For multiple-cores, if running model this might happen very frequently. To avoid this, Melodie makes the first
        shot, which means running one of the runs out of one scenario, by main-process. Only when first shot completes
        will the subprocesses be launched.


        :return: None
        """
        from MelodieInfra.parallel.parallel_manager import ParallelManager

        t0 = time.time()
        self.pre_run()

        t1 = time.time()
        parallel_manager_data = {
            "model": (
                self.model_cls.__name__,
                self.model_cls.__module__,
            ),
            "scenario": (
                self.scenario_cls.__name__,
                self.scenario_cls.__module__,
            ),
            "trainer": (
                self.__class__.__name__,
                self.__class__.__module__,
            ),
            "data_loader": (
                self.df_loader_cls.__name__,
                self.df_loader_cls.__module__,
            )
            if self.df_loader_cls is not None
            else None,
        }
        parallel_manager = ParallelManager(
            cores, configs=(parallel_manager_data, self.config.to_dict())
        )
        parallel_manager.run("simulator")
        try:
            logger.info(f"Melodie will run for {len(self.scenarios)} times!.")
            first_run = False
            tasks_count = 0
            for scenario in self.scenarios:
                for id_run in range(scenario.run_num):
                    if not first_run:
                        self.run_model(
                            self.config,
                            scenario,
                            id_run,
                            self.model_cls,
                        )
                        first_run = True
                    else:
                        parallel_manager.put_task((id_run, scenario.to_json(), None))
                        tasks_count += 1

            for i in range(tasks_count):
                parallel_manager.get_result()
                logger.info(f"finished {i+1} tasks!")
            t2 = time.time()
            logger.info(
                f"Melodie completed all runs, time elapsed totally {t2 - t0}s, and {t2 - t1}s for running."
            )
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except Exception:
            import traceback

            traceback.print_exc()
        finally:
            logger.info("quit parallel manager!")
            parallel_manager.close()
