from Melodie import Scenario
from tutorial.CovidContagion.source import data_info


class CovidScenario(Scenario):
    def setup(self):
        self.period_num = 0
        self.agent_num = 0
        self.initial_infected_percentage = 0.0
        self.young_percentage = 0.0
        self.network_type = ""
        self.network_param_k = 0
        self.network_param_p = 0.0
        self.network_param_m = 0
        self.infection_prob = 0.0
        self.setup_age_group_params()

    def setup_age_group_params(self):
        df = self.get_dataframe(data_info.id_age_group)
        self.ag0_prob_s1_s1 = df.at[0, "prob_s1_s1"]
        self.ag0_prob_s1_s2 = df.at[0, "prob_s1_s2"]
        self.ag0_prob_s1_s3 = df.at[0, "prob_s1_s3"]
        self.ag1_prob_s1_s1 = df.at[1, "prob_s1_s1"]
        self.ag1_prob_s1_s2 = df.at[1, "prob_s1_s2"]
        self.ag1_prob_s1_s3 = df.at[1, "prob_s1_s3"]

    def get_state_transition_prob(self, id_age_group: int) -> tuple:
        if id_age_group == 0:
            return self.ag0_prob_s1_s1, self.ag0_prob_s1_s2, self.ag0_prob_s1_s3
        elif id_age_group == 1:
            return self.ag1_prob_s1_s1, self.ag1_prob_s1_s2, self.ag1_prob_s1_s3
        else:
            raise ValueError("This person has wierd age group.")

    def get_network_params(self):
        if self.network_type == "barabasi_albert_graph":
            network_params = {"m": self.network_param_m}
        elif self.network_type == "watts_strogatz_graph":
            network_params = {"k": self.network_param_k, "p": self.network_param_p}
        else:
            raise NotImplementedError
        return network_params
