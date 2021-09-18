from Melodie.agent import Agent
from Melodie.agent_manager import AgentManager


def test_agent_manager_type_hinting():
    class TestAgent(Agent):
        pass

    am = AgentManager(TestAgent, 0)
    am.add(TestAgent())
