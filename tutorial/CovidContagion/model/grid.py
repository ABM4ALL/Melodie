from Melodie import Spot, Grid, AgentList
import tutorial.CovidContagion.model.data_info as df_info


class CovidSpot(Spot):
    def setup(self):
        self.stay_prob = 0.0


class CovidGrid(Grid):
    def config_grid(self):
        self.set_size(self.scenario.grid_x_size, self.scenario.grid_y_size)
        self.set_multi(True)

    def setup(self):
        self.set_spot_attribute(
            "stay_prob", self.scenario.get_matrix(df_info.grid_stay_prob)
        )
