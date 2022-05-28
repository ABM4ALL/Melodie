from Melodie import Grid, GridAgent


class CovidAgent(GridAgent):
    def setup(self):
        self.x = 0
        self.y = 0
        self.category = 0
        self.condition = 0

    def move(self, grid: "Grid"):
        self.x, self.y = grid.rand_move(self, self.category, 1, 1)
