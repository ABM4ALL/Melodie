from .types import List, Dict, Optional
from .agent import Element


class Environment(Element):
    def __init__(self):
        super().__init__()
        self.model: Optional['Model'] = None
        self.scenario: Optional['Scenario'] = None

    def setup(self):
        """
        The setup method of the environment.
        Use `self.scenario` to get the parameters from the scenario.
        :return:
        """
        pass

    def to_dict(self, properties: List[str]) -> Dict:
        """
        Dump Environment to a plain dict.
        :param properties:
        :return:
        """
        if properties is None:
            properties = self.__dict__.keys()
        d = {}
        for property in properties:
            d[property] = self.__dict__[property]
        return d

    def _setup(self):
        self.setup()


__all__ = ['Environment']
