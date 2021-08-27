import pytest
from Melodie.Agent import Agent


def test_params():
    class NewAgent(Agent):
        params = ["a", "b"]

        def __init__(self):
            super().__init__(None)
            self.a = 123
            self.b = 34.0

    agent = NewAgent()
    agent.set_params({"a": 456, "b": 34.0})
    assert agent.a == 456
