from Melodie import Scenario


class CovidScenario(Scenario):
    """
    Scenario class that defines network parameters and contagion probabilities.
    """

    def setup(self):
        self.period_num: int = 0
        self.run_num: int = 1
        self.agent_num: int = 0
        
        # Network parameters
        self.network_type: str = ""
        self.network_param_k: int = 0
        self.network_param_p: float = 0.0
        self.network_param_m: int = 0
        
        # Contagion parameters
        self.initial_infected_percentage: float = 0.0
        self.infection_prob: float = 0.0
        self.recovery_prob: float = 0.0

    def load_data(self):
        """
        Load reference data.
        Note: The '.csv' extension must be explicit if using the default loader.
        """
        self.health_states = self.load_dataframe("ID_HealthState.csv")

    def get_network_params(self):
        """
        Helper to format network parameters for NetworkX based on the network type.
        """
        if self.network_type == "barabasi_albert_graph":
            return {"m": self.network_param_m}
        elif self.network_type == "watts_strogatz_graph":
            return {"k": self.network_param_k, "p": self.network_param_p}
        else:
            raise NotImplementedError(f"Unsupported network_type {self.network_type}")
