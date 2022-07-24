from Melodie import Scenario


class CovidScenario(Scenario):
    def setup(self):
        self.periods = 0
        self.agent_num = 0
        self.grid_x_size = 0
        self.grid_y_size = 0
        self.initial_infected_percentage = 0.0
        self.infection_probability = 0.0
