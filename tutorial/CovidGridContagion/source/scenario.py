from tutorial.CovidContagion.source.scenario import CovidScenario


class CovidGridScenario(CovidScenario):
    def setup(self):
        self.period_num = 0
        self.agent_num = 0
        self.grid_x_size = 0
        self.grid_y_size = 0
        self.initial_infected_percentage = 0.0
        self.young_percentage = 0.0
        self.infection_prob = 0.0
        self.setup_age_group_params()
