from Melodie import DataCollector


class CovidDataCollector(DataCollector):
    """Collect micro and macro results for the grid contagion model."""

    def setup(self) -> None:
        self.add_agent_property("agents", "health_state")
        self.add_environment_property("num_susceptible")
        self.add_environment_property("num_infected")
        self.add_environment_property("num_recovered")
