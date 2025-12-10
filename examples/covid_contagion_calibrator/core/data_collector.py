from Melodie import DataCollector


class CovidDataCollector(DataCollector):
    def setup(self) -> None:
        """
        Registers which properties of agents and the environment should be recorded.

        In this minimal example we record:
        - micro-level results: each agent's ``health_state``;
        - macro-level results: population counts on the environment
          (``num_susceptible``, ``num_infected``, ``num_recovered``).
        """
        self.add_agent_property("agents", "health_state")
        self.add_environment_property("num_susceptible")
        self.add_environment_property("num_infected")
        self.add_environment_property("num_recovered")

