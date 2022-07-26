from Melodie import Spot, Grid


class CovidSpot(Spot):
    def setup(self):
        self.stay_prob = 0.0


class CovidGrid(Grid):

    # Grid功能：shuffle agent的位置？
    # 能不能站同一个格子？

    # def load_matrix(file_name: str)

    # def setup_spots_attribute(spot_attribute: str, file_name: str)
    #     matrix = load_matrix(file_name: str)
    #     assert size is right
    #     assert no missing values
    #     assert data_types of all values are same
    #     for x, y ...

    def setup_spots(self):
        # self.setup_spots_attribute('stay_prob', 'grid_stay_prob.xlsx')
        ...

