
from Melodie import Calibrator, GeneticAlgorithm
from .environment import CovidEnvironment


class CovidCalibrator(Calibrator):

    def setup(self):
        self.add_property('initial_infected_percentage')
        self.add_property('infection_probability')

        self.watched_env_properties = ['accumulated_infection']
        self.algorithm_cls = GeneticAlgorithm

    def distance(self, environment: CovidEnvironment):
        print("infection_rate", environment.accumulated_infection / environment.scenario.agent_num)
        return abs(environment.accumulated_infection / environment.scenario.agent_num - 0.75)

    def convert_distance_to_fitness(self, distance: float):
        return 1 - distance
