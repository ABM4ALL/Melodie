from abc import ABC
from typing import Callable, List, Tuple, Union, Dict


class SearchingAlgorithm(ABC):
    def setup(self):
        pass

    def set_parameters(self, parameters_num: int):
        pass

    def set_parameters_agents(self, agent_num: int, agent_params: int):
        pass

    def optimize(self, fitness: Callable):
        pass


class AlgorithmParameters:
    """
    Learning scenario is used in Trainer and Calibrator for trainer/calibrator parameters.
    """

    class Parameter:
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
            parameters.extend(
                [(parameter.min, parameter.max) for parameter in self.parameters]
            )
        return parameters

    def parse_params(self, record: Dict[str, Union[int, float]]):
        max_values = {
            name[: len(name) - len("_max")]: value
            for name, value in record.items()
            if name.endswith("_max")
        }
        min_values = {
            name[: len(name) - len("_min")]: value
            for name, value in record.items()
            if name.endswith("_min")
        }
        print(max_values, min_values)
        assert len(max_values) == len(min_values)
        for k in max_values.keys():
            self.parameters.append(
                AlgorithmParameters.Parameter(k, min_values[k], max_values[k])
            )
