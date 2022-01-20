# 1. 注册一张目标表，里面的数据结构不要求
#  - 单个数
#  - 一条或甚至多条序列

# 2. 根据表里的数据定义distance function
#  - calibrator里面的@abstractmethod (loss, similar to fitness function in trainer, but it is opposite)
#  - Conceptually, "distance" is opposite to "fitness", so in the GA behind, we need to convert the DanDiaoXing.


# 这时候也注册一张scenario的表，但就只有一行了，标记待calibrate的参数，以及这些参数的范围
# simulator跟trainer合作时候，scenarios和training_scenarios都可以有好多行（虽然后者可能只用一行），组合着train；
# 但是，simulator跟calibrator合作的时候，scenarios和calibrating_target就只有唯一的一对一组合关系。
import numpy as np

from Melodie import Calibrator
import sqlalchemy

from .environment import CovidEnvironment
from .scenario import CovidScenario


class CovidCalibrator(Calibrator):

    def setup(self):
        self.add_property('initial_infected_percentage')
        self.add_property('infection_probability')

        self.watched_env_properties = ['accumulated_infection']

    def distance(self, environment: CovidEnvironment):
        print("infection_rate", environment.accumulated_infection / environment.current_scenario().agent_num)
        return (environment.accumulated_infection / environment.current_scenario().agent_num - 0.5) ** 2

    def convert_distance_to_fitness(self, distance: float):
        return 1 - distance

    def register_scenario_dataframe(self):
        scenarios_dict = {"periods": sqlalchemy.Integer(),
                          "agent_num": sqlalchemy.Integer(),
                          "grid_x_size": sqlalchemy.Integer(),
                          "grid_y_size": sqlalchemy.Float(),
                          "initial_infected_percentage": sqlalchemy.Float(),
                          "infection_probability": sqlalchemy.Integer()}
        self.load_dataframe('scenarios', 'simulator_scenarios.xlsx', scenarios_dict)

    def register_static_dataframes(self) -> None:
        # load由calibrator得到的表
        self.load_dataframe('calibrator_scenarios', 'calibrator_scenarios.xlsx', {})
        self.load_dataframe('calibrator_params_scenarios', 'calibrator_params_scenarios.xlsx', {})

    def register_generated_dataframes(self):

        def init_condition(initial_infected_percentage: float):
            condition = 0
            rand = np.random.uniform(0, 1)
            if rand <= initial_infected_percentage:
                condition = 1
            else:
                pass
            return condition

        with self.new_table_generator('agent_params', lambda scenario: scenario.agent_num) as g:
            def generator_func(scenario: CovidScenario):
                return {'id': g.increment(),
                        'x_pos': np.random.randint(0, scenario.grid_x_size),
                        'y_pos': np.random.randint(0, scenario.grid_y_size),
                        'condition': init_condition(scenario.initial_infected_percentage)}

            g.set_row_generator(generator_func)
            g.set_column_data_types({'id': sqlalchemy.Integer(),
                                     'x_pos': sqlalchemy.Integer(),
                                     'y_pos': sqlalchemy.Integer(),
                                     'condition': sqlalchemy.Integer()})
