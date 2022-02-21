import numpy as np
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from Melodie import AgentList

if TYPE_CHECKING:
    from .agent import AspirationAgent
    from .environment import AspirationEnvironment


class AspirationUpdateStrategy(ABC):

    def __init__(self, average_profit: float):
        self.average_profit = average_profit

    @abstractmethod
    def aspiration_update(self, agent: 'AspirationAgent') -> None:
        pass


class HistoricalAspirationUpdateStrategy(AspirationUpdateStrategy):

    def aspiration_update(self, agent: 'AspirationAgent') -> None:
        agent.aspiration_level = agent.historical_aspiration_update_param * agent.profit + \
                                 (1 - agent.historical_aspiration_update_param) * agent.aspiration_level


class SocialAspirationUpdateStrategy(AspirationUpdateStrategy):

    def aspiration_update(self, agent: 'AspirationAgent') -> None:
        agent.aspiration_level = self.average_profit