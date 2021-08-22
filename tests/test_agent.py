import pytest
from Melodie.Agent import Agent


def test_fib_10():
    assert (Agent().fibonacci(10) == 55)


def test_fib_not_20():
    assert (Agent().fibonacci(20) != 20)


def test_params():
    class NewAgent(Agent):
        params = ["a", "b"]

        def __init__(self):
            super().__init__()
            self.a = 123
            self.b = 34.0

    agent = NewAgent()
    agent.setup({"a": 456, "b": 34.0})
    assert agent.a == 456
