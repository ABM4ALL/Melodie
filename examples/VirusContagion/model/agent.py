from Melodie import GridAgent


class CovidAgent(GridAgent):
    def setup(self):
        self.x = 0
        self.y = 0
        self.category = 0
        self.condition = 0

    def move(self):
        self.rand_move_agent(1, 1)
