from typing import (
    Type,
    List,
    Optional,
    ClassVar,
    Iterator,
    Union,
    Dict,
    TYPE_CHECKING,
)
import pandas as pd
import logging
from Melodie import (
    Model,
    Scenario,
    Config,
    GACalibratorParams,
    DataFrameLoader,
)
from Melodie.algorithms import SearchingAlgorithm
from .algorithms.ga_calibrator import GACalibratorAlgorithm
from .algorithms.meta import GACalibratorAlgorithmMeta
from .simulator import BaseModellingManager

if TYPE_CHECKING:
    from Melodie.boost.basics import Environment
logger = logging.getLogger(__name__)


class Calibrator(BaseModellingManager):
    """
    Calibrator
    """

    def __init__(
        self,
        config: "Config",
        scenario_cls: "Optional[ClassVar[Scenario]]",
        model_cls: "Optional[ClassVar[Model]]",
        df_loader_cls: ClassVar["DataFrameLoader"],
        processors=1,
    ):
        super().__init__(
            config=config,
            scenario_cls=scenario_cls,
            model_cls=model_cls,
            df_loader_cls=df_loader_cls,
        )
        self.processes = processors
        self.training_strategy: "Optional[Type[SearchingAlgorithm]]" = None
        self.container_name: str = ""

        self.properties: List[str] = []
        self.watched_env_properties: List[str] = []
        self.recorded_agent_properties: Dict[str, List[str]] = {}
        self.algorithm: Optional[Type[SearchingAlgorithm]] = None
        self.algorithm_instance: Iterator[List[float]] = {}

        self.model: Optional[Model] = None

        self.current_algorithm_meta = GACalibratorAlgorithmMeta()
        self.df_loader: Optional["DataFrameLoader"] = None
        self.df_loader_cls = df_loader_cls

    def setup(self):
        pass

    def generate_scenarios(self) -> List["Scenario"]:
        """
        Generate scenario objects by the parameter from static tables or scenarios_dataframe.

        :return:
        """
        return self.df_loader.generate_scenarios_from_dataframe("calibrator_scenarios")

    def get_params_scenarios(self) -> Dict:
        """
        Get the parameters of calibrator parameters from the registered dataframe.

        :return:
        """
        calibrator_scenarios_table = self.get_registered_dataframe(
            "calibrator_params_scenarios"
        )
        assert isinstance(
            calibrator_scenarios_table, pd.DataFrame
        ), "No learning scenarios table specified!"
        return calibrator_scenarios_table.to_dict(orient="records")

    def calibrate(self):
        """
        The main method for calibrator.
        :return:
        """
        self.setup()
        self.pre_run()

        scenario_cls = GACalibratorParams
        for scenario in self.scenarios:
            self.current_algorithm_meta.calibrator_scenario_id = scenario.id
            calibration_scenarios = self.get_params_scenarios()
            for calibrator_scenario in calibration_scenarios:
                calibrator_scenario = scenario_cls.from_dataframe_record(
                    calibrator_scenario
                )
                self.current_algorithm_meta.calibrator_params_id = (
                    calibrator_scenario.id
                )
                for trainer_path_id in range(calibrator_scenario.number_of_path):
                    self.current_algorithm_meta.path_id = trainer_path_id

                    self.run_once_new(scenario, calibrator_scenario)

    def run_once_new(self, scenario, calibration_scenario: GACalibratorParams):
        self.algorithm = GACalibratorAlgorithm(
            self.properties,
            self.watched_env_properties,
            {},
            calibration_scenario,
            self.target_function,
            manager=self,
            processors=self.processes,
        )
        self.algorithm.run(scenario, self.current_algorithm_meta)

    def target_function(self, env: "Environment") -> Union[float, int]:
        raise NotImplementedError

    def add_environment_calibrating_property(self, prop: str):
        """
        Add a property to be calibrated, and the property should be a property of environment.

        :param prop:
        :return:
        """
        assert (
            prop not in self.properties
        ), f'Property "{prop}" is already in the calibrating training_properties!'
        self.properties.append(prop)

    def add_environment_result_property(self, prop: str):
        """
        Add a property of environment to be recorded in the calibration voyage.

        :param prop:
        :return:
        """
        assert prop not in self.watched_env_properties
        self.watched_env_properties.append(prop)
