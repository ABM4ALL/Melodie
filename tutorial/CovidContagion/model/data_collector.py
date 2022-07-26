from Melodie import DataCollector


class CovidDataCollector(DataCollector):
    def setup(self):
        self.add_agent_property("agents", "x")
        self.add_agent_property("agents", "y")
        self.add_agent_property("agents", "health_state")
        self.add_environment_property("s0")
        self.add_environment_property("s1")
        self.add_environment_property("s2")
        self.add_environment_property("s3")
        self.add_environment_property("s4")


