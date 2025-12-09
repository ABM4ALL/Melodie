from Melodie import DataCollector


class RPSDataCollector(DataCollector):
    """
    A custom data collector for the Rock-Paper-Scissors model.

    It is configured to save detailed agent-level data about each game round
    (e.g., opponent, action, result, payoff) as well as the final evolved
    strategy shares. It also records the environment-level total payoff.
    """

    def setup(self) -> None:
        self.add_agent_property("agents", "id_competitor")
        self.add_agent_property("agents", "action")
        self.add_agent_property("agents", "n_rock")
        self.add_agent_property("agents", "n_paper")
        self.add_agent_property("agents", "n_scissors")
        self.add_agent_property("agents", "result")
        self.add_agent_property("agents", "payoff")
        self.add_agent_property("agents", "accumulated_payoff")
        self.add_agent_property("agents", "share_rock")
        self.add_agent_property("agents", "share_paper")
        self.add_agent_property("agents", "share_scissors")
        self.add_environment_property("total_accumulated_payoff")

