from typing import Dict, Any


class Element:
    def set_params(self, params: Dict[str, Any]):
        """

        :param params:
        :return:
        """
        for paramName, paramValue in params.items():
            assert (
                paramName in self.__dict__.keys()
            ), f"param named {paramName}, value {paramValue} not in Agent.params:{self.__dict__.keys()}"
            setattr(self, paramName, paramValue)
