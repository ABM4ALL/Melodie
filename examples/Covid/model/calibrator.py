from Melodie import Calibrator, GeneticAlgorithmCalibrator
from .environment import CovidEnvironment


class CovidCalibrator(Calibrator):

    def setup(self):
        self.add_environment_calibrating_property('initial_infected_percentage')
        self.add_environment_calibrating_property('infection_probability')

        # self.watched_env_properties = ['accumulated_infection']
        self.add_environment_result_property('accumulated_infection')
        self.algorithm_cls = GeneticAlgorithmCalibrator

    def distance(self, environment: CovidEnvironment):
        print("infection_rate", environment.accumulated_infection / environment.scenario.agent_num)
        return abs(environment.accumulated_infection / environment.scenario.agent_num - 0.75)

    def convert_distance_to_fitness(self, distance: float):
        print('fitness', 1 - distance)
        return 1 - distance
