import random
from typing import TYPE_CHECKING

from Melodie import GridAgent

if TYPE_CHECKING:
    from Melodie import AgentList
    from .scenario import CovidScenario
    from .grid import CovidGrid, CovidSpot
    from .network import CovidNetwork


class CovidAgent(GridAgent):
    scenario: "CovidScenario"
    grid: "CovidGrid"
    spot: "CovidSpot"

    def set_category(self):
        self.category = 0

    def setup(self):
        self.x = 0
        self.y = 0
        self.age_group = 0
        self.health_state = 0
        self.vaccination_trust_state = 0

    def move(self):
        spot: "CovidSpot" = self.grid.get_spot(self.x, self.y)
        stay_prob = spot.stay_prob
        if random.uniform(0, 1) < stay_prob:
            pass
        else:
            move_radius = self.scenario.get_move_radius(self.age_group)
            self.rand_move(move_radius, move_radius)

    def infect_from_neighbors(self, grid: "CovidGrid", agents: "AgentList[CovidAgent]"):
        infection_prob = self.scenario.get_infection_prob(self.health_state)
        if infection_prob > 0:
            neighbors_info = grid.get_neighbors_info(self.x, self.y)  # 还是叫get_neighbors吧，加上info也不知道具体是什么info
            for agent_id, agent_category in neighbors_info:
                neighbor_agent: "CovidAgent" = agents.get_agent(agent_id)
                if neighbor_agent.health_state == 1 and random.uniform(0, 1) < infection_prob:
                    self.health_state = 1
                    break

    def update_vaccination_trust_from_ad(self):
        if self.vaccination_trust_state == 0:
            if random.uniform(0, 1) <= self.scenario.vaccination_ad_success_prob:
                self.vaccination_trust_state = 1

    def update_vaccination_trust_from_neighbors(self, network: "CovidNetwork"):
        if self.vaccination_trust_state == 0:
            neighbors = network.get_neighbors()
            for neighbor in neighbors:
                pass

    def take_vaccination(self):
        if self.health_state == 0:
            if random.uniform(0, 1) <= self.scenario.vaccination_action_prob:
                self.health_state = 4

    def health_state_transition(self):
        if self.health_state == 1:
            (
                prob_s1_s1,
                prob_s1_s2,
                prob_s1_s3,
            ) = self.scenario.get_state_transition_prob(self.age_group)
            rand = random.uniform(0, 1)
            if rand <= prob_s1_s1:
                pass
            elif prob_s1_s1 < rand <= prob_s1_s1 + prob_s1_s2:
                self.health_state = 2
            else:
                self.health_state = 3