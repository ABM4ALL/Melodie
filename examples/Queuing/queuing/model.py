from Melodie.Agent import Agent
from Melodie.Model import Model
from Melodie.AgentManager import AgentManager


class WaitingModel(Model):
    def __init__(self, agent_class):
        self.agent_manager = AgentManager(agent_class, 100)
