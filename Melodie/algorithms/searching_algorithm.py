from abc import ABC
from typing import Callable, List, Tuple


class SearchingAlgorithm(ABC):
    def setup(self):
        pass

    def set_parameters(self, parameters_num: int):
        pass

    def set_parameters_agents(self, agent_num: int, agent_params: int):
        pass

    def optimize(self, fitness: Callable):
        pass

    def optimize_multi_agents(self, fitness, scenario):
        pass


class AlgorithmParameters:
    """
    Learning scenario is used in Trainer and Calibrator for trainer/calibrator parameters.
    """

    class Parameter():
        def __init__(self, name: str, min: float, max: float):
            self.name = name
            self.min = min
            self.max = max

        def __repr__(self):
            return f"<{self.__class__.__name__} '{self.name}', range ({self.min}, {self.max})>"

    def __init__(self, id: int, number_of_path: int):
        self.id: int = id
        self.number_of_path: int = number_of_path
        self.parameters: List[AlgorithmParameters.Parameter] = []

    def get_agents_parameters_range(self, agent_num) -> List[Tuple[float, float]]:
        parameters = []
        for agent_id in range(agent_num):
            parameters.extend([(parameter.min, parameter.max) for parameter in self.parameters])
        return parameters
