from Melodie import Calibrator, GeneticAlgorithmCalibrator
from .environment import CovidEnvironment


class CovidCalibrator(Calibrator):

    def setup(self):
        self.add_environment_calibrating_property('infection_probability')
        self.add_environment_result_property('accumulated_infection')
        self.algorithm_cls = GeneticAlgorithmCalibrator

    def distance(self, environment: CovidEnvironment):
        print("infection_rate", environment.accumulated_infection / environment.scenario.agent_num)
        return (environment.accumulated_infection / environment.scenario.agent_num - 0.75) ** 2

