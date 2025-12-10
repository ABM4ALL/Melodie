from Melodie import Scenario


class CovidScenario(Scenario):
    """
    Defines the parameters for each simulation run of the virus contagion model.
    It inherits from the base `Melodie.Scenario`.

    Special Melodie attributes (automatically populated from `SimulatorScenarios`):
    - `id`: A unique identifier for the scenario.
    - `run_num`: How many times to repeat this scenario (for stochastic models). Defaults to 1.
    - `period_num`: How many simulation steps (periods) for each run. Defaults to 0.
    """

    def setup(self) -> None:
        """
        Declares custom scenario parameters for type hinting and clarity.
        These are automatically populated from columns in `SimulatorScenarios`.
        """
        self.agent_num: int = 0
        self.initial_infected_percentage: float = 0.0
        self.infection_prob: float = 0.0
        self.recovery_prob: float = 0.0

    def load_data(self) -> None:
        """
        This method is automatically called by Melodie after scenario parameters are set.
        It is the recommended place to load all static input dataframes, making them
        accessible via `self.scenario.*` from `Model`, `Agent`, and `Environment`.
        """
        self.health_states = self.load_dataframe("ID_HealthState.csv")
