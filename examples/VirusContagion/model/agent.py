from Melodie import Agent, Grid, GridAgent


class CovidAgent(GridAgent):
    category = 0
    def setup(self):
        self.x = 0
        self.y = 0
        self.condition = 0

    def move(self, grid: 'Grid'):
        self.x, self.y = grid.rand_move(self, 0, 1, 1)
        # print(self.x, self.y)
        return
