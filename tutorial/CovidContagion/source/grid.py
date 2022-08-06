from Melodie import Spot, Grid
import tutorial.CovidContagion.source.data_info as df_info


class CovidSpot(Spot):
    def setup(self):
        self.stay_prob = 0.0


class CovidGrid(Grid):

    def setup(self):
        self.set_spot_attribute("stay_prob", self.scenario.get_matrix(df_info.grid_stay_prob))


