import logging
from typing import Dict, Any
import warnings

class Element:
    def set_params(self, params: Dict[str, Any], asserts_key_exist=True):
        """

        :param params:
        :return:
        """
        for paramName, paramValue in params.items():
            msg = f"param named {paramName}, value {paramValue} not in Agent.params:{self.__dict__.keys()}"
            if paramName not in self.__dict__.keys():
                if asserts_key_exist:
                    raise ValueError(msg)
                else:
                    warnings.warn(msg)
            

            setattr(self, paramName, paramValue)
