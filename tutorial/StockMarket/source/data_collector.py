from Melodie import DataCollector


class StockDataCollector(DataCollector):
    def setup(self):
        self.add_agent_property("agents", "x")
        self.add_environment_property("s4")
