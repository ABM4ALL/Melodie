from Melodie import Agent
from .scenario import _ALIAS_Scenario


class _ALIAS_Agent(Agent):
    scenario: _ALIAS_Scenario

    def setup(self):
        pass
