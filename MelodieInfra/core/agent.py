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
        This is the initialization method where agent properties can be declared.

        "Declaration" means defining properties with initial values, such as 0, 0.0,
        or "". For example:

        .. code-block:: python

            class NewAgent(Agent)
                def setup(self):
                    self.int_property = 0
                    self.float_property = 0.0
                    self.str_property = ""

        While it is possible to define properties with complex data structures like
        dicts, lists, or sets, their values can be difficult for the `DataCollector`
        to record automatically.

        This method is executed automatically at the end of the agent's ``__init__``
        method.

        :return: None
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
