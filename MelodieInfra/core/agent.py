from typing import TYPE_CHECKING, Any, Dict, List, Optional


class Element:
    def set_params(self, params: Dict[str, Any]):
        """
        :param params:
        :return:
        """
        for item in params.items():
            paramName, paramValue = item
            # assert (
            #     paramName in self.__dict__.keys()
            # ), f"param named {paramName}, value {paramValue} not in Agent.params:{self.__dict__.keys()}"
            if paramName in self.__dict__.keys():
                setattr(self, paramName, paramValue)

    def to_dict(self, properties: List[str] = None) -> Dict:
        """
        Dump to a plain dict.

        :param properties:
        """
        if properties is None:
            properties = self.__dict__.keys()
        d = {}
        for property in properties:
            d[property] = self.__dict__[property]
        return d

    def to_json(self, properties: List[str] = None) -> Dict:
        """
        Dump to a json serializable dict

        :param properties:
        """
        if properties is None:
            properties = self.__dict__.keys()
        d = {}
        for property in properties:
            if property in self._unserializable_props_:
                continue
            d[property] = self.__dict__[property]
        return d


class Agent(Element):
    _unserializable_props_ = ("model", "scenario")

    def __init__(self, agent_id: int):
        super().__init__()
        self.id = agent_id
        self.scenario: Optional["Scenario"] = None
        self.model: Optional["Model"] = None

    def setup(self):
        """
        This is the initialization method, declare properties here.
        Here, "Declare" is to define properties with zero as initial value, such as:
        ```python
        class NewAgent(Agent)
            def setup(self):
                self.int_property = 0
                self.float_property = 0.0
                self.str_property = ""
        ```
        It is also fine to define properties with complex data structure such as dict/list/set, but the values in the
        complex data structure is hard to be recorded by the `DataCollector`
        This method is executed at the end of the `__init__` method of the corresponding agent container.
        :return:
        """
        pass

    def __repr__(self) -> str:
        d = {}
        for item in self.__dict__.items():
            k, v = item
            if not k.startswith("_"):
                d[k] = v
        # d = {k: v for k, v in self.__dict__.items() if
        #      not k.startswith("_")}
        return "<%s %s>" % (self.__class__.__name__, d)


__all__ = ["Element", "Agent"]
