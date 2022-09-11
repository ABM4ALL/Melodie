import random
from typing import TYPE_CHECKING

from Melodie import GridAgent
from tutorial.CovidContagion.source.agent import CovidAgent

if TYPE_CHECKING:
    from Melodie import AgentList
    from .grid import CovidSpot, CovidGrid
    from .scenario import CovidGridScenario


class CovidGridAgent(CovidAgent, GridAgent):
    scenario: "CovidGridScenario"
    grid: "CovidGrid"
    spot: "CovidSpot"

    def set_category(self):
        self.category = 0

    def move(self):
        spot: "CovidSpot" = self.grid.get_spot(self.x, self.y)
        stay_prob = spot.stay_prob
        if random.uniform(0, 1) > stay_prob:
            move_radius = 1
            self.rand_move_agent(move_radius, move_radius)

    def infection(self, agents: "AgentList[CovidAgent]"):
        neighbors = self.grid.get_neighbors(self)
        for neighbor_category, neighbor_id in neighbors:
            neighbor_agent: "CovidGridAgent" = agents.get_agent(neighbor_id)
            if neighbor_agent.health_state == 1:
                if random.uniform(0, 1) < self.scenario.infection_prob:
                    self.health_state = 1
                    break
