import random
from typing import TYPE_CHECKING

from Melodie import GridAgent

if TYPE_CHECKING:
    from .grid import CovidGrid, CovidSpot
    from .scenario import CovidScenario
    from Melodie import AgentList


class CovidAgent(GridAgent):
    """
    An agent capable of moving on a grid and spreading infection to neighbors.
    Inherits from GridAgent to gain spatial attributes (x, y) and methods.
    """

    scenario: "CovidScenario"
    grid: "CovidGrid"
    spot: "CovidSpot"

    def set_category(self) -> None:
        """
        Set the category of the agent. 
        Melodie uses this to manage different groups of agents.
        """
        self.category = 0

    def setup(self) -> None:
        """
        Initialize agent attributes.
        """
        self.x: int = 0
        self.y: int = 0
        # Health state: 0 = Susceptible, 1 = Infected, 2 = Recovered
        self.health_state: int = 0

    def move(self) -> None:
        """
        Move the agent based on the property of the current spot.
        The agent has a probability (1 - stay_prob) to move to a random neighboring cell.
        """
        current_spot = self.grid.get_spot(self.x, self.y)
        if random.random() > current_spot.stay_prob:
            # Move randomly within a radius of 1 cell (Moore neighborhood)
            self.rand_move_agent(x_range=1, y_range=1)

    def infect_neighbors(self, agents: "AgentList[CovidAgent]") -> None:
        """
        If infected, try to infect susceptible neighbors.
        """
        if self.health_state != 1:
            return

        # Get neighbors within a radius of 1
        neighbors = self.grid.get_neighbors(self, radius=1)
        
        for neighbor_id in neighbors:
            # In Melodie, get_neighbors returns a list of agent IDs (or objects depending on config).
            # Here we assume it returns IDs or we access the agent list directly.
            # Actually, standard Grid.get_neighbors returns list of (agent_category, agent_id).
            category, agent_id = neighbor_id
            neighbor: "CovidAgent" = agents.get_agent(agent_id)
            
            if neighbor.health_state == 0:
                if random.random() < self.scenario.infection_prob:
                    neighbor.health_state = 1

    def recover(self) -> None:
        """
        If infected, there is a chance to recover.
        """
        if self.health_state == 1 and random.random() < self.scenario.recovery_prob:
            self.health_state = 2
