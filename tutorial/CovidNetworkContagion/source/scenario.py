from tutorial.CovidContagion.source.scenario import CovidScenario


class CovidNetworkScenario(CovidScenario):

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

    def get_network_params(self):
        if self.network_type == "barabasi_albert_graph":
            network_params = {"m": self.network_param_m}
        elif self.network_type == "watts_strogatz_graph":
            network_params = {"k": self.network_param_k, "p": self.network_param_p}
        else:
            raise NotImplementedError
        return network_params
