from Melodie import Spot, Grid


class CovidSpot(Spot):
    def setup(self):
        self.stay_prob = 0.0


class CovidGrid(Grid):

    # 需要让grid能够访问scenario

    # 能不能站同一个格子？

    # def load_matrix(file_name: str)

    # def setup_spots_attribute(spot_attribute: str, file_name: str)
    #     matrix = load_matrix(file_name: str)
    #     assert size is right
    #     assert no missing values
    #     assert data_types of all values are same
    #     for x, y ...

    def setup(self):
        # self.setup_spots_attribute('stay_prob', 'grid_stay_prob.xlsx')
        # self.setup_agent_locations(agents: 'AgentList[Covid]')
        ...
