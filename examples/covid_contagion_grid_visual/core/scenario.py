from Melodie import Scenario
import numpy as np


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
        
        # Generate a uniform stay_prob matrix dynamically based on grid size
        # Ensure data type is float (standard Python float preferred by JSON serializers)
        self.stay_prob_matrix = np.full(
            (self.grid_x_size, self.grid_y_size), 
            fill_value=0.5,
            dtype=float
        )
