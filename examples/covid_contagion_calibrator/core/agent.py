import random
from Melodie import Agent


class CovidAgent(Agent):
    def setup(self) -> None:
        """
        Initializes the agent's state.
        `health_state`: 0 = susceptible, 1 = infected, 2 = recovered.
        """
        self.health_state: int = 0  # All agents start as susceptible.

    def health_state_update(self, recovery_prob: float) -> None:
        """
        Agent-level logic for transitioning from infected to recovered.
        """
        if self.health_state == 1 and random.random() < recovery_prob:
            self.health_state = 2

