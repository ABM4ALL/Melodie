from Melodie import Agent, Grid


class CovidAgent(Agent):

    def setup(self):
        self.x_pos = 0
        self.y_pos = 0
        self.condition = 0
        self.condition_next = 0

    def move(self, grid: 'Grid'):
        self.x_pos, self.y_pos = grid.rand_move(self.id, 'agent_list', 1, 1)
        return
