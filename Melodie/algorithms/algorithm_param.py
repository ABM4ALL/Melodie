from typing import List, Tuple, Union, Dict


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

    def __init__(self, id: int, path_num: int):
        self.id: int = id
        self.path_num: int = path_num
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
        assert len(max_values) == len(min_values)
        for k in max_values.keys():
            self.parameters.append(
                AlgorithmParameters.Parameter(k, min_values[k], max_values[k])
            )

    def bounds(self, param_names: List[str]) -> Tuple[List[float], List[float]]:
        """
        Get the lower bounds and upper bounds of each parameter in the order of param_names.

        :param param_names:  A series of parameter names indicating the order to get the bounds
        :return: lower bounds, upper bounds
        """
        ub_list: List[float] = []
        lb_list: List[float] = []
        for param_name in param_names:
            params = list(filter(lambda p: p.name == param_name, self.parameters))
            if len(params) == 1:
                param = params[0]
                ub_list.append(param.max)
                lb_list.append(param.min)
            else:
                raise Exception(f"Parameters error: {params}, {self.parameters}")
        return lb_list, ub_list
