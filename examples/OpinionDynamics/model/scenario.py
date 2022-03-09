
from Melodie import Scenario


class OpinionDynamicsScenario(Scenario):

    def setup(self):
        self.periods = 0
        self.agent_num = 0
        self.network_param_k = 0
        self.network_param_p = 0.0
        self.opinion_level_min = 0.0
        self.opinion_level_max = 0.0
        self.opinion_radius_min = 0.0
        self.opinion_radius_max = 0.0
        self.communication_prob = 0.0
        self.relative_agreement_param = 0.0


