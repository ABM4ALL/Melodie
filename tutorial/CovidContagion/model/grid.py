from Melodie import Spot, Grid, AgentList
import tutorial.CovidContagion.model.dataframe_info as df_info


class CovidSpot(Spot):
    def setup(self):
        self.stay_prob = 0.0


class CovidGrid(Grid):

    # 自动调用：
    def config_grid(self):
        self.set_size(self.scenario.grid_x_size,
                      self.scenario.grid_y_size)
        self.set_multi(True)

    # def load_matrix(file_name: str)

    # def setup_spots_attribute(spot_attribute: str, file_name: str)
    #     matrix = load_matrix(file_name: str)
    #     assert size is right
    #     assert no missing values
    #     assert data_types of all values are same
    #     for x, y ...
    def setup_agents(self, agents: "AgentList"):
        self.setup_agent_locations(agents)

    def setup(self):
        # self.setup_spots_attribute('stay_prob', 'grid_stay_prob.xlsx')
        # self.setup_agent_locations(agents: 'AgentList[Covid]')
        matrix = self.scenario.get_matrix(df_info.grid_stay_prob)
        self.set_spot_attribute('stay_prob', matrix)
