from typing import List, Dict, Any


class Element:
    """
    Basic element, the parent class of Agent, Environment and Managers.

    Element.params: stores the initial param names
    Element.results: stores the values should be saved into database every step
    Element.types: stores the data type. for sqlite it can be :{"a":"INTEGER","txt":"TEXT"}
    """
    def set_params(self, params: Dict[str, Any]):
        """
        Set property which was declared at Element.params
        :param params:
        :return:
        """
        for paramName, paramValue in params.items():
            assert paramName in self.__dict__.keys(), f"param named {paramName}, value {paramValue} not in Agent.params:{self.__dict__.keys()}"
            setattr(self, paramName, paramValue)

