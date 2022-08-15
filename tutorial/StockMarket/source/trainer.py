from Melodie import Trainer
from .agent import StockAgent


class StockTrainer(Trainer):
    def setup(self):
        self.add_agent_training_property(
            "agents",
            ["fundamentalist_weight"],
            lambda scenario: list(range(scenario.agent_num)),
        )

    def collect_data(self):
        self.add_environment_property("open")
        self.add_environment_property("close")
        self.add_agent_property("agents", "stock_account")
        self.add_agent_property("agents", "cash_account")
        self.add_agent_property("agents", "wealth_period")

    def utility(self, agent: "StockAgent"):
        return agent.wealth_period
