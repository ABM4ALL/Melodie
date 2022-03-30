from Melodie import GridAgent, Grid
from .scenario import ShellingModelScenario


class BaseGridAgent(GridAgent):
    scenario: ShellingModelScenario
    category: int

    def satisfy_with_neighbors(self, grid: Grid):
        neighbors = grid.get_neighbors(self.x, self.y)
        count = 0
        count_other_category = 0
        for neighbor in neighbors:
            agents = grid.get_agents(neighbor[0], neighbor[1])  # Get neighbor with same type
            if len(agents) == 1:
                if agents[0].category == self.category:
                    count += 1
                else:
                    count_other_category += 1
        return count >= self.scenario.desired_sametype_neighbors
        # return count >= self.scenario.desired_sametype_neighbors

    def move(self, grid: Grid):
        self.x, self.y = grid.choose_empty_place()


class ShellingModelAgentTypeA(BaseGridAgent):
    scenario: ShellingModelScenario

    def setup(self):
        self.category = 0
        pass


class ShellingModelAgentTypeB(BaseGridAgent):
    scenario: ShellingModelScenario

    def setup(self):
        self.category = 1
        pass
