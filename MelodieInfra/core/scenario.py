from .types import Optional, Union
from .agent import Element


class Scenario(Element):
    """
    Scenario contains a set of parameters used in simulation model.
    It is created before the initialization of ``Model``.

    """

    def __init__(self, id_scenario: Optional[Union[int, str]] = None):
        """
        :param id_scenario: the id of scenario. if None, this will be self-increment from 0 to scenarios_number-1
        """
        super().__init__()
        self._parameters = []
        self.manager: Union["Calibrator", "Simulator", None] = None
        self.id = id_scenario
        self.run_num = 1
        self.period_num = 0

    def copy(self) -> "Scenario":
        """
        Copy current scenario to a new scenario.

        :return: New scenario object.
        """
        new_scenario = self.__class__()
        for property_name in self.__dict__.keys():
            property = self.__dict__[property_name]
            setattr(new_scenario, property_name, property)
        for parameter in self._parameters:
            parameter.init = getattr(self, parameter.name)
        return new_scenario

    def setup(self):
        """
        Setup method, be sure to inherit it on the custom scenario class.
        """
        pass

    def to_dict(self):
        """
        Convert this scenario object to a dict.

        :return: A ``dict``, ``property_name->property_value``
        """
        d = {}
        for k in self.__dict__.keys():
            v = self.__dict__[k]
            d[k] = v
        return d

    def to_json(self):
        """
        Convert this scenario to a dict without concerning non-serializable properties.

        :return: a ``dict``, ``property_name->property_value``, without non-serializable properties
        """
        d = {}
        for k in self.__dict__.keys():
            if k not in ["manager"]:
                d[k] = self.__dict__[k]
        return d

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.__dict__}>"


__all__ = ['Scenario']
