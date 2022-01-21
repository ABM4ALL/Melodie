# Calibrator是用simulation-based calibration的方法校准【选出的一部分】enviornment parameters
# 先对所有参数做敏感性分析，找出重要的calibrate，
# 给要calibrate的参数设定空间，然后sampling，再搜索。
# 搜索的时候涉及两部分：
# 第一，定义simulated output和real data之间的距离，这个有不同度量方法；
# 第二，返回某个参数组合的“距离”后，怎么迭代搜索到下一组参数组合。
# register.rst, calibrator, trainer都涉及反复跑模型，也都涉及注册表。可能可以在它们三者之上定义一个父类，它们三者是不同的running mode。

import abc
from typing import Type, Callable, List, Optional, ClassVar, Iterator, Union, Tuple, Dict
import copy
import numpy as np
import pandas as pd
import logging
from Melodie import Model, Scenario, Simulator, Config, Agent, create_db_conn, GACalibrationScenario
from Melodie.algorithms import GeneticAlgorithm, TrainingAlgorithm
from Melodie.basic import MelodieExceptions

logger = logging.getLogger(__name__)


class Calibrator(Simulator, abc.ABC):
    """
    Calibrator
    """

    # 用来individually calibrate agents' parameters，
    # 只考虑针对strategy中参数的off-line learning。online-learning的部分千奇百怪，暂时交给用户自己来吧。
    def __init__(self, config: 'Config', scenario_class: 'Optional[ClassVar[Scenario]]',
                 model_class: 'Optional[ClassVar[Model]]'):
        super().__init__()
        self.config = config
        self.training_strategy: 'Optional[Type[TrainingAlgorithm]]' = None
        self.container_name: str = ''

        self.properties: List[str] = []
        self.watched_env_properties: List[str] = []
        self.algorithm: Optional[Type[TrainingAlgorithm]] = None
        self.algorithm_instance: Iterator[List[float]] = {}

        self.model_class: Optional[ClassVar[Model]] = model_class
        self.model: Optional[Model] = None
        self.scenario_class: Optional[ClassVar[Scenario]] = scenario_class

        self.current_algorithm_meta = {
            "scenario_id": 0,
            "learning_scenario_id": 1,
            "learning_path_id": 0,
            "generation_id": 0
        }

    def setup(self):
        pass

    def generate_scenarios(self) -> List['Scenario']:
        """
        Generate scenario objects by the parameter from static tables or scenarios_dataframe.
        :return:
        """
        return self.generate_scenarios_from_dataframe('calibrator_scenarios')

    def calibrate(self):
        self.setup()
        self.pre_run()
        calibrator_scenarios_table = self.get_registered_dataframe('calibrator_params_scenarios')
        assert isinstance(calibrator_scenarios_table, pd.DataFrame), "No learning scenarios table specified!"

        for scenario in self.scenarios:
            self.current_algorithm_meta['scenario_id'] = scenario.id
            calibration_scenarios = calibrator_scenarios_table.to_dict(orient="records")
            for calibration_scenario in calibration_scenarios:
                calibration_scenario = GACalibrationScenario.from_dataframe_record(calibration_scenario)
                self.current_algorithm_meta['calibration_scenario_id'] = calibration_scenario.id
                for learning_path_id in range(calibration_scenario.number_of_path):
                    self.current_algorithm_meta['learning_path_id'] = learning_path_id

                    self.learn_once(scenario, calibration_scenario)

    def learn_once(self, scenario, calibration_scenario: GACalibrationScenario):

        scenario.manager = self
        self.model = self.model_class(self.config, scenario)
        self.model.setup()

        self.algorithm = GeneticAlgorithm(calibration_scenario.calibration_generation,
                                          calibration_scenario.strategy_population,
                                          calibration_scenario.mutation_prob,
                                          calibration_scenario.strategy_param_code_length)
        self.algorithm.parameter_names = self.properties
        self.algorithm.parameters = [(parameter.min, parameter.max) for parameter in calibration_scenario.parameters]
        self.algorithm.parameters_num = len(self.algorithm.parameters)

        self.algorithm_instance = self.algorithm.optimize(self.fitness, scenario)

        for i in range(calibration_scenario.calibration_generation):
            self.current_algorithm_meta['generation_id'] = i
            logger.info(f"===================Training step {i + 1}=====================")
            strategy_population, params, fitness, meta = self.algorithm_instance.__next__()

            calibrator_result_cov = copy.deepcopy(meta['env_params_cov'])
            calibrator_result_cov.update(meta['env_params_mean'])
            calibrator_result_cov['fitness_mean'] = meta['fitness_mean']
            calibrator_result_cov['fitness_cov'] = meta['fitness_cov']

            calibrator_result_cov.update(self.current_algorithm_meta)
            create_db_conn(self.config).write_dataframe('calibrator_result_cov',
                                                        pd.DataFrame([calibrator_result_cov]))

    def set_algorithm(self, algorithm: Type[TrainingAlgorithm]):
        """

        :param algorithm:
        :return:
        """
        assert isinstance(algorithm, TrainingAlgorithm)
        self.algorithm = algorithm

    def add_property(self, prop: str):
        """
        Add a property to be calibrated.
        It should be a property of environment.
        :param prop:
        :return:
        """
        assert prop not in self.properties
        self.properties.append(prop)

    def fitness(self, params, scenario: Union[Type[Scenario], Scenario], **kwargs) -> float:
        for i, prop_name in enumerate(self.properties):
            assert scenario.__getattribute__(prop_name) is not None
            scenario.__setattr__(prop_name, params[i])
        scenario_properties_dict = {prop_name: scenario.__dict__[prop_name] for prop_name in self.properties}
        self.model = self.model_class(self.config, scenario)
        self.model.setup()
        meta = kwargs['meta']
        environment_record_dict = {}
        environment_record_dict.update(self.current_algorithm_meta)

        self.model.run()

        env = self.model.environment

        fitness = self.convert_distance_to_fitness(self.distance(env))
        MelodieExceptions.Assertions.NotNone('fitness', fitness)
        environment_record_dict.update(scenario_properties_dict)
        environment_record_dict['chromosome_id'] = meta['chromosome_id']
        environment_record_dict.update({
            prop: env.__dict__[prop] for prop in self.watched_env_properties
        })
        environment_record_dict['fitness'] = fitness

        create_db_conn(self.config). \
            write_dataframe('calibrator_result',
                            pd.DataFrame([environment_record_dict]),
                            if_exists="append")
        return fitness

    @abc.abstractmethod
    def distance(self, environment) -> float:
        return -1.0

    @abc.abstractmethod
    def convert_distance_to_fitness(self, distance: float):
        return -1.0
