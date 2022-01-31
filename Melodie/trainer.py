import abc
import math
import time
from typing import Type, List, Optional, ClassVar, Iterator, Union, Tuple
from abc import ABC
import copy
import numpy as np
import pandas as pd

from Melodie import Model, Scenario, Simulator, Config, Agent, create_db_conn, GATrainerScenario
from Melodie.algorithms import GeneticAlgorithm, TrainingAlgorithm
from .simulator import BaseModellingManager
from .dataframe_loader import DataFrameLoader


class Trainer(BaseModellingManager):
    """
    Individually calibrate agents' parameters
    """

    def __init__(self, config: 'Config', scenario_cls: 'Optional[ClassVar[Scenario]]',
                 model_cls: 'Optional[ClassVar[Model]]', df_loader_cls: 'Optional[ClassVar[DataFrameLoader]]'):
        super().__init__(config=config,
                         scenario_cls=scenario_cls,
                         model_cls=model_cls,
                         df_loader_cls=df_loader_cls)

        self.training_strategy: 'Optional[Type[TrainingAlgorithm]]' = None
        self.container_name: str = ''
        self.property_name: str = ''
        self.properties: List[str] = []

        self.environment_properties: List[str] = []

        self.algorithm: Optional[Type[TrainingAlgorithm]] = None
        self.algorithm_instance: Iterator[List[float]] = {}

        self.model: Optional[Model] = None

        self.agent_result_columns = [
            "scenario_id", "learning_scenario_id",
            "trainer_path_id", "generation_id",
            "chromosome_id",
            "agent_id",
            "para_1", "para_2", "para_3", "fitness"
        ]
        self.agent_result = []

        self.current_algorithm_meta = {
            "scenario_id": 0,
            "learning_scenario_id": 1,
            "trainer_path_id": 0,
            "generation_id": 0}

    def setup(self):
        pass

    def train(self):
        """
        The main method of Trainer.


        :return:
        """
        self.setup()
        self.pre_run()
        trainer_scenarios_table = self.get_registered_dataframe('trainer_params_scenarios')
        assert isinstance(trainer_scenarios_table, pd.DataFrame), "No learning scenarios table specified!"

        for scenario in self.scenarios:
            self.current_algorithm_meta['scenario_id'] = scenario.id
            trainer_scenarios = trainer_scenarios_table.to_dict(orient="records")
            for trainer_scenario in trainer_scenarios:
                trainer_scenario = GATrainerScenario.from_dataframe_record(trainer_scenario)
                self.current_algorithm_meta['learning_scenario_id'] = trainer_scenario.id
                for trainer_path_id in range(trainer_scenario.number_of_path):
                    self.current_algorithm_meta['trainer_path_id'] = trainer_path_id

                    self.run_once(scenario, trainer_scenario)

    def run_once(self, scenario, trainer_scenario: GATrainerScenario):

        scenario.manager = self
        self.model = self.model_cls(self.config, scenario)
        self.model.setup()
        agents_num = len(self.model.__getattribute__(self.container_name))
        agents = self.model.__getattribute__(self.container_name)
        self.algorithm = GeneticAlgorithm(trainer_scenario.training_generation, trainer_scenario.strategy_population,
                                          trainer_scenario.mutation_prob, trainer_scenario.strategy_param_code_length)
        self.algorithm.set_parameters_agents(agents_num,
                                             len(self.properties),
                                             self.properties,
                                             self.environment_properties)
        self.algorithm.parameters = trainer_scenario.get_parameters_range(agents_num)

        self.algorithm.parameters_value = []
        for agent in agents:
            self.algorithm.parameters_value.extend([agent.__getattribute__(name) for name in self.properties])

        self.algorithm_instance = self.algorithm.optimize_multi_agents(self.fitness, scenario)

        for i in range(trainer_scenario.training_generation):
            self.current_algorithm_meta['generation_id'] = i
            print(f"===================Training step {i + 1}=====================")
            if i == 0:
                strategy_population, params, fitness, meta = self.algorithm_instance.__next__()
            else:
                strategy_population, params, fitness, meta = self.algorithm_instance.send(len(agents))
            agent_training_cov = copy.deepcopy(meta['agent_learning_cov'])
            env_training_cov = copy.deepcopy(meta['env_learning_cov'])

            for d in agent_training_cov:
                d.update(self.current_algorithm_meta)
            env_training_cov.update(self.current_algorithm_meta)
            create_db_conn(self.config).write_dataframe('agent_learning_cov', pd.DataFrame(agent_training_cov))
            create_db_conn(self.config).write_dataframe('env_learning_cov', pd.DataFrame([env_training_cov]))

    def set_algorithm(self, algorithm: Type[TrainingAlgorithm]):
        """

        :param algorithm:
        :return:
        """
        assert isinstance(algorithm, TrainingAlgorithm)
        self.algorithm = algorithm

    def add_property(self, container: str, prop: str):
        """
        :param container:
        :param prop:
        :return:
        """
        assert prop not in self.properties
        self.container_name = container
        self.properties.append(prop)

    def get_agent_params(self, all_params, agent_id: int):
        agent_params = {}
        for j, prop_name in enumerate(self.properties):
            agent_params[prop_name] = all_params[agent_id * len(self.properties) + j]
        return agent_params

    def fitness(self, params, scenario: Union[Type[Scenario], Scenario], **kwargs) -> Tuple[np.ndarray, dict]:
        self.model = self.model_cls(self.config, scenario)
        self.model.setup()
        agents = self.model.__getattribute__(self.container_name)
        agents_params_list = []
        environment_record_dict = {}
        environment_record_dict.update(self.current_algorithm_meta)

        for i, agent in enumerate(agents):
            agents_dic = {
                "agent_id": agent.id,
            }
            agents_dic.update(kwargs['meta'])
            agents_dic.update(self.current_algorithm_meta)
            assert i == agent.id
            agent_params = self.get_agent_params(params, agent.id)
            for j, prop_name in enumerate(self.properties):
                setattr(agent, prop_name, agent_params[prop_name])
            agents_dic.update(agent_params)
            agents_params_list.append(agents_dic)
        self.model.run()

        agents = self.model.__getattribute__(self.container_name)
        env = self.model.environment
        environment_properties_dict = {prop_name: env.__dict__[prop_name] for prop_name in self.environment_properties}
        environment_record_dict.update(environment_properties_dict)
        fitness_list = []
        for i, agent in enumerate(agents):
            agent_fitness = self.fitness_agent(agent)
            fitness_list.append(agent_fitness)
            agents_params_list[agent.id]['fitness'] = agent_fitness
        create_db_conn(self.config).write_dataframe('agent_learning_result', pd.DataFrame(agents_params_list),
                                                    if_exists="append")
        create_db_conn(self.config).write_dataframe('env_learning_result', pd.DataFrame([environment_record_dict]),
                                                    if_exists="append")
        return np.array(fitness_list), environment_properties_dict

    def fitness_agent(self, agent: Type[Agent]) -> float:
        """
        返回float，只要保证值越大、策略越好即可。
        无需保证>=0
        :param agent:
        :return:
        """
        pass

    def generate_scenarios(self):
        assert self.table_loader is not None
        return self.table_loader.generate_scenarios('trainer')
