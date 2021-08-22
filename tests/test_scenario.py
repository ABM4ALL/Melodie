import pytest
from Melodie.ScenarioManager import Scenario


def test_scenario():
    class NewScenario(Scenario):
        results = ["ID", "agentNum"]

        def __init__(self):
            self.ID = 0
            self.agentNum = 100
    s = NewScenario()
    assert s.toDict()["ID"] == 0
    assert s.toDict()["agentNum"] == 100
