"""
This data stores the run function for model running, storing global variables and other services.
"""
import abc
import logging
import threading
import time
from multiprocessing import Pool
from typing import ClassVar, TYPE_CHECKING, Optional, List, Tuple

import pandas as pd

import Melodie.visualizer
from .basic import show_prettified_warning
from .basic.exceptions import MelodieExceptions
from .dataframe_loader import DataFrameLoader
from .visualizer import Visualizer

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .model import Model
    from .scenario_manager import Scenario
    from .config import Config

else:
    from .scenario_manager import Scenario
    from .config import Config
    from .db import create_db_conn


class BaseModellingManager(abc.ABC):
    """
    Base class of Simulator/Trainer/Calibrator.
    """

    def __init__(
        self,
        config: Config,
        scenario_cls: ClassVar["Scenario"],
        model_cls: ClassVar["Model"],
        df_loader_cls: ClassVar[DataFrameLoader] = None,
    ):
        self.config: Optional[Config] = config
        self.scenario_cls = scenario_cls
        self.model_cls = model_cls

        self.scenarios: Optional[List["Scenario"]] = None
        self.df_loader_cls: Optional[ClassVar[DataFrameLoader]] = df_loader_cls
        self.df_loader: Optional[DataFrameLoader] = None
        if df_loader_cls is not None:
            assert issubclass(df_loader_cls, DataFrameLoader), df_loader_cls

    def get_registered_dataframe(self, table_name) -> pd.DataFrame:
        """
        Get a static table.
        :param table_name:
        :return:
        """
        if self.df_loader is None:
            raise MelodieExceptions.Data.NoDataframeLoaderDefined()
        if table_name not in self.df_loader.registered_dataframes:
            raise MelodieExceptions.Data.StaticTableNotRegistered(
                table_name, list(self.df_loader.registered_dataframes.keys())
            )

        return self.df_loader.registered_dataframes[table_name]

    def subworker_prerun(self):
        self.df_loader: DataFrameLoader = self.df_loader_cls(
            self, self.config, self.scenario_cls
        )
        self.df_loader.as_sub_worker = True
        self.df_loader.register_scenario_dataframe()
        self.df_loader.register_static_dataframes()
        self.df_loader.register_generated_dataframes()

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
            self.df_loader = self.df_loader_cls(self, self.config, self.scenario_cls)

            self.df_loader.register_scenario_dataframe()
            self.df_loader.register_static_dataframes()
            self.df_loader.register_generated_dataframes()

        self.scenarios = self.generate_scenarios()
        if self.scenarios is None:
            MelodieExceptions.Scenario.NoValidScenarioGenerated(self.scenarios)

    @abc.abstractmethod
    def generate_scenarios(self):
        pass


class Simulator(BaseModellingManager):
    def __init__(
        self,
        config: Config,
        scenario_cls: "ClassVar[Scenario]",
        model_cls: "ClassVar[Model]",
        df_loader_cls: "ClassVar[DataFrameLoader]" = None,
    ):
        super(Simulator, self).__init__(
            config=config,
            scenario_cls=scenario_cls,
            model_cls=model_cls,
            df_loader_cls=df_loader_cls,
        )
        self.server_thread: threading.Thread = None
        self.visualizer: Optional[Visualizer] = None

    def generate_scenarios(self) -> List["Scenario"]:
        """
        Generate scenarios from the dataframe_loader
        :return:
        """
        if self.df_loader is None:
            raise MelodieExceptions.Data.NoDataframeLoaderDefined()
        return self.df_loader.generate_scenarios("simulator")

    def run_model(
        self, config, scenario, run_id, model_class: ClassVar["Model"], visualizer=None
    ):
        """

        :return:
        """
        logger.info(f"Running {run_id + 1} times in scenario {scenario.id}.")
        t0 = time.time()

        model: Model = model_class(
            config, scenario, run_id_in_scenario=run_id, visualizer=visualizer
        )
        if visualizer is not None:
            visualizer._model = model

        model.setup()

        if visualizer is not None:
            visualizer.start()

        t1 = time.time()
        logger.info(f"Model setup, taking {t1 - t0} seconds.")
        logger.info(f"Model is running...")
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
            f"Running {run_id + 1} in scenario {scenario.id} completed with time elapsed(seconds):\n"
            f"    model-setup   \t {round(model_setup_time, 6)}\n"
            f"    model-run     \t {round(model_run_time, 6)}\n"
            f"    data-collect  \t {round(data_collect_time, 6)}\n"
        )
        logger.info(info)

    def setup(self):
        pass

    def run(self):
        """
        Main function for running model!
        """
        t0 = time.time()
        Visualizer.enabled = False
        self.setup()
        if self.visualizer is not None:
            show_prettified_warning(
                "You are using `Simulator.run()` method to run model, but you have also defined visualizer.\n"
                "If you would like to visualize this model, please use `Simulator.run_visual()` "
                "instead of `Simulator.run` "
            )

        self.pre_run()
        logger.info("Loading scenarios and static tables...")
        t1 = time.time()
        for scenario_index, scenario in enumerate(self.scenarios):
            for run_id in range(scenario.number_of_run):
                self.run_model(
                    self.config, scenario, run_id, self.model_cls, visualizer=None
                )

            logger.info(
                f"{scenario_index + 1} of {len(self.scenarios)} scenarios has completed."
            )

        t2 = time.time()
        logger.info(
            f"Melodie completed all runs, time elapsed totally {t2 - t0}s, and {t2 - t1}s for running."
        )

    def run_visual(self):
        """
        Main function for running model with studio.
        """
        t0 = time.time()

        self.setup()
        self.pre_run()

        t1 = time.time()
        logger.info(f"Simulator start up cost: {t1 - t0}s")
        while True:
            logger.info(
                f"Visualizer interactive paramerters for this scenario are: {self.visualizer.scenario_param}"
            )

            scenario = self.scenarios[0].copy()
            scenario.manager = self
            for k, v in self.visualizer.scenario_param.items():
                scenario.__setattr__(k, v)
            logger.info(f"Scenario parameters: {scenario.to_dict()}")
            try:
                self.visualizer.current_scenario = scenario  # set studio scenario.
                self.run_model(
                    self.config, scenario, 0, self.model_cls, visualizer=self.visualizer
                )
            except Melodie.visualizer.MelodieModelReset:

                self.visualizer.reset()
                logger.info("Model reset.")

        t2 = time.time()
        logger.info(
            f"Melodie completed all runs, time elapsed totally {t2 - t0}s, and {t2 - t1}s for running."
        )

    def run_parallel(self, cores: int = 2):
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
        shot, which means running one of the runs out of one scenario, by main-process. Only when first shot completes
        will the subprocesses be launched.


        :return:
        """
        t0 = time.time()
        self.pre_run()

        t1 = time.time()
        logger.info("Loading scenarios and static tables...")
        pool = Pool(cores)

        parameters: List[Tuple] = []
        for scenario_index, scenario in enumerate(self.scenarios):
            for run_id in range(scenario.number_of_run):
                params = (
                    self.config,
                    scenario,
                    run_id,
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
