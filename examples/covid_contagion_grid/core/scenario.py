from Melodie import Scenario


class CovidScenario(Scenario):
    """
    Manages simulation parameters and loads input data.
    """

    def setup(self) -> None:
        """
        Define the parameters that will be loaded from SimulatorScenarios.csv.
        """
        # Core parameters
        self.agent_num: int = 0
        self.initial_infected_percentage: float = 0.0
        self.infection_prob: float = 0.0
        self.recovery_prob: float = 0.0
        # Grid dimensions
        self.grid_x_size: int = 0
        self.grid_y_size: int = 0

    def load_data(self) -> None:
        """
        Load auxiliary data files.
        """
        # Load health state definitions (optional mapping, good for reference)
        self.health_states = self.load_dataframe("ID_HealthState.csv")
        
        # Load the stay_prob matrix for the grid spots
        # This file should contain a matrix matching the grid dimensions
        self.stay_prob_matrix = self.load_matrix("Parameter_GridStayProb.csv")
