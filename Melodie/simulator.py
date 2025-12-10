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
from typing import List, Literal, Optional, Tuple, Type

import pandas as pd

from MelodieInfra import (
    Config,
    DBConn,
    MelodieExceptions,
    MelodieGlobalConfig,
    create_db_conn,
    get_sqlite_filename,
    show_prettified_warning,
)
from MelodieInfra.db.db import db_conn

from .data_loader import DataLoader
from .model import Model
from .scenario_manager import Scenario
from .visualizer import BaseVisualizer, MelodieModelReset

logger = logging.getLogger(__name__)


class BaseModellingManager(abc.ABC):
    """
    An abstract base class for managers that orchestrate model execution, such
    as :class:`~Melodie.Simulator`, :class:`~Melodie.Trainer`, and
    :class:`~Melodie.Calibrator`.

    This class provides the core functionalities for initializing scenarios and
    loading data.
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
        Get a static DataFrame from the data loader.

        :param table_name: The name of the table as registered in the
            :class:`~Melodie.DataLoader`.
        :return: A pandas DataFrame.
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
        Get a static matrix from the data loader.

        :param matrix_name: The name of the matrix as registered in the
            :class:`~Melodie.DataLoader`.
        :return: A numpy ndarray.
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
        A pre-run routine for parallel worker processes.

        This method initializes the data loader and generates scenarios for a
        worker process without clearing existing output data, which should only
        be done by the main process.
        """
        if self.df_loader_cls is not None:
            self.data_loader: DataLoader = self.df_loader_cls(
                self, self.config, self.scenario_cls, as_sub_worker=True
            )

        self.scenarios = self.generate_scenarios()

    def clear_output_tables(self):
        """
        Clear all generated files in the output directory.
        """
        output_path = self.config.output_tables_path()
        if os.path.exists(output_path):
            shutil.rmtree(output_path)
        os.mkdir(output_path)

    def pre_run(self, clear_output_data=True):
        """
        The main pre-run routine for the manager.

        This method should be called before the main execution loop. It
        initializes the database and output directories, sets up the data
        loader, and generates the scenarios to be run.

        :param clear_output_data: If ``True``, all existing output tables in the
            database and CSV files in the output directory will be deleted.
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

        standard_table_map = {
            "SimulatorScenarios": "simulator_scenarios",
            "TrainerScenarios": "trainer_scenarios",
            "CalibratorScenarios": "calibrator_scenarios",
            "CalibratorParamsScenarios": "calibrator_params_scenarios",
            "TrainerParamsScenarios": "trainer_params_scenarios",
        }
        if self.data_loader is not None:
            for table_name, attr_name in standard_table_map.items():
                if table_name in self.data_loader.registered_dataframes:
                    df = self.data_loader.registered_dataframes[table_name]
                    for scenario in self.scenarios:
                        setattr(scenario, attr_name, df)

        if self.scenarios is None or len(self.scenarios) == 0:
            raise MelodieExceptions.Scenario.NoValidScenarioGenerated(self.scenarios)

    @abc.abstractmethod
    def generate_scenarios(self) -> List[Scenario]:
        """
        An abstract method for generating a list of scenarios.

        This method must be implemented by subclasses to define how scenarios
        are created, typically by loading them from a scenario table.
        """
        pass

    def _write_to_table(
        self, kind: Literal["csv", "sql"], table_name: str, data: pd.DataFrame
    ):
        """
        (Internal) Write a pandas DataFrame to a specified table.

        Depending on the ``kind``, the table will be written to a CSV file in
        the output directory or to a table in the database.
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
                data.to_csv(csv_file, mode="a", header=False, index=False)
            else:
                data.to_csv(csv_file, index=False)
        else:
            raise NotImplementedError


class SimulatorMeta:
    """
    (Internal) A metadata class for the simulator.
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
    The ``Simulator`` is the primary manager for running model simulations.

    It orchestrates the entire simulation process, including initializing the
    model and scenarios, running the simulation for each scenario, and handling
    data collection and visualization.
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
        :param config: The project :class:`~Melodie.Config` object.
        :param scenario_cls: The :class:`~Melodie.Scenario` subclass for the model.
        :param model_cls: The :class:`~Melodie.Model` subclass for the model.
        :param data_loader_cls: The :class:`~Melodie.DataLoader` subclass for the
            model.
        :param visualizer_cls: The :class:`~Melodie.BaseVisualizer` subclass for
            the model, if visualization is needed.
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
        Generate scenarios using the data loader.

        This method calls the data loader to generate a list of scenario objects
        based on the ``SimulatorScenarios`` table.

        :return: A list of ``Scenario`` objects.
        """
        if self.data_loader is None:
            raise MelodieExceptions.Data.NoDataframeLoaderDefined()

        return self.data_loader.generate_scenarios("Simulator")

    def run_model(
        self, config, scenario, id_run, model_class: Type["Model"], visualizer=None
    ):
        """
        Run a single simulation for one scenario and one run ID.
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
        A hook for custom simulator setup. This method is called before ``pre_run``.
        """
        pass

    def run(self):
        """
        The main entry point for running batch simulations without visualization.

        This method iterates through all defined scenarios and their specified
        number of runs, executing the model for each.
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
        The main entry point for running a simulation with visualization.

        This method starts the visualizer and runs the model for the first
        scenario in a loop, allowing for interactive parameter changes and
        resets from the web interface.
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
        Run simulations in parallel using multiple processes.

        This method uses Python's ``multiprocessing.Pool`` to distribute the
        simulation runs across a specified number of CPU cores.

        To avoid race conditions during database table creation, the first
        simulation run is executed in the main process. This ensures that all
        necessary tables are created before the parallel workers start writing
        to them.

        :param cores: The number of CPU cores to use for parallel execution. It is
            recommended to set this to the number of **physical cores** on your
            machine for optimal performance.
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
        An alternative parallel execution method using a custom ParallelManager.

        .. note::
            This method is experimental and may be deprecated in the future.
            ``run_parallel`` is the recommended method for parallel execution.

        This method uses a more complex architecture involving ``rpyc`` for
        inter-process communication, which can be more robust in certain
        environments. Like ``run_parallel``, it executes the first run in the
        main process to ensure database initialization.

        :param cores: The number of CPU cores to use.
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
