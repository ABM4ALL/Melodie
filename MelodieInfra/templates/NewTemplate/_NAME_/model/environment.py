from Melodie import Environment
from .scenario import _ALIAS_Scenario


class _ALIAS_Environment(Environment):
    scenario: _ALIAS_Scenario

    def setup(self):
        pass
