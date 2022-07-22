from Melodie import DataCollector


class CovidDataCollector(DataCollector):
    def setup(self):
        self.add_agent_property("agent_list", "x")
        self.add_agent_property("agent_list", "y")
        self.add_agent_property("agent_list", "condition")
        self.add_environment_property("accumulated_infection")
