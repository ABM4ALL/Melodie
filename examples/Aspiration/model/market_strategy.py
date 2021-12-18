
import numpy as np
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from Melodie import AgentList

if TYPE_CHECKING:
    from.agent import AspirationAgent
    from.environment import AspirationEnvironment

class MarketStrategy(ABC):

    def __init__(self, agent_list: 'AgentList[AspirationAgent]', environment: 'AspirationEnvironment'):
        self.agent_list = agent_list
        self.environment = environment

    @abstractmethod
    def calculate_profit(self, agent: 'AspirationAgent') -> None:
        pass

class NonCompetitiveMarketStrategy(MarketStrategy):

    def calculate_profit(self, agent: 'AspirationAgent') -> None:
        mean = self.environment.market_profit_mean
        sigma = self.environment.market_profit_sigma
        agent.profit = agent.technology + np.random.normal(mean, sigma)
        agent.account += agent.profit
        agent.profit_aspiration_difference = agent.profit - agent.aspiration_level
        pass
