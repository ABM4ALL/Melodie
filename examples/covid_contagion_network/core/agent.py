from Melodie import NetworkAgent
from typing import TYPE_CHECKING
import random

if TYPE_CHECKING:
    from Melodie import AgentList


class CovidAgent(NetworkAgent):
    """
    Network-based Covid agent with basic SIR states.
    
    Attributes:
        health_state (int): 0=Susceptible, 1=Infected, 2=Recovered.
        category (int): Agent category (0 for all agents in this simple model).
    """

    def setup(self):
        """
        Initialize agent properties.
        """
        self.health_state: int = 0
        self.category: int = 0

    def set_category(self):
        """
        Required by NetworkAgent to determine the category ID.
        We use a single category (0) for simplicity.
        """
        self.category = 0

    def seed_infection(self, initial_infected_percentage: float):
        """
        Randomly infect the agent based on the initial percentage.
        """
        if random.random() < initial_infected_percentage:
            self.health_state = 1
