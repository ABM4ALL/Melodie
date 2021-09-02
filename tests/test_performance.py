import time

from Melodie.Agent import Agent
from Melodie.AgentManager import AgentManager


class TestAgent(Agent):
    def setup(self):
        self.val2 = 0
        self.val = 0
        self.text = ''
        self.indiced = {
            ("val",): lambda agent: agent.val,

        }
        self.mapped = {
            ("val", "text"): lambda agent: agent.val
        }


class A():
    def __init__(self):
        self.a = 0

    pass


def test_performance():
    t0 = time.time()
    al = AgentManager(TestAgent, length=10)
    agent = al.agents[0]
    agent.val2 = 0

    a = A()
    for i in range(1_000_000):
        agent.val = i
    t1 = time.time()
    for i in range(1_000_000):
        agent.val2 = i
    t2 = time.time()
    for i in range(1_000_000):
        a.a = i
    t3 = time.time()
    print(t1 - t0, t2 - t1, t3 - t2)
