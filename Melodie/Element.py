from typing import List, Dict, Any


class Element:
    """
    Basic element, the parent class of Agent, Environment and Managers.

    Element.params: stores the initial param names
    Element.results: stores the values should be saved into database every step
    Element.types: stores the data type. for sqlite it can be :{"a":"INTEGER","txt":"TEXT"}
    """
    params: List[str] = []
    results: List[str] = []
    types: Dict[str, str] = {}

    def setup(self, params: Dict[str, Any]):
        allParamNames = self.params
        for paramName, paramValue in params.items():
            assert paramName in allParamNames, f"param named {paramName}, value {paramValue} not in Agent.params:{allParamNames}"
            setattr(self, paramName, paramValue)
