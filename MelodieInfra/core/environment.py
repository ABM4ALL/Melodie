from typing import Dict, List, Optional

from .agent import Element


class Environment(Element):
    def __init__(self):
        super().__init__()
        self.model: Optional["Model"] = None
        self.scenario: Optional["Scenario"] = None

    def setup(self):
        """
        Set up the environment at the beginning of a simulation run.

        This method is called after the scenario has been initialized, so scenario
        parameters can be accessed via ``self.scenario``. It is intended for
        initializing environment-level properties or states.
        """
        pass

    def to_dict(self, properties: List[str]) -> Dict:
        """
        Convert a list of environment properties to a dictionary.

        :param properties: A list of property names to include in the dictionary.
        """
        if properties is None:
            properties = self.__dict__.keys()
        d = {}
        for property in properties:
            d[property] = self.__dict__[property]
        return d

    def _setup(self):
        self.setup()


__all__ = ["Environment"]
