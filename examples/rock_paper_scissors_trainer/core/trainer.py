from Melodie import Trainer

from examples.rock_paper_scissors_trainer.core.agent import RPSAgent


class RPSTrainer(Trainer):
    """
    A custom Trainer for evolving agents' strategies in the Rock-Paper-Scissors model.

    This trainer uses a genetic algorithm to tune the three strategy parameters
    for each agent. The goal is to maximize the agent's final accumulated payoff,
    which serves as the fitness function for the evolutionary process.
    """

    def setup(self) -> None:
        # Configures the trainer to target the three strategy parameters for all
        # agents in the 'agents' list.
        self.add_agent_training_property(
            "agents",
            ["strategy_param_1", "strategy_param_2", "strategy_param_3"],
            lambda scenario: list(range(scenario.agent_num)),
        )

    def collect_data(self) -> None:
        # Specifies which properties to save during the training process.
        # This allows for analysis of how strategies and outcomes evolve over generations.
        self.add_agent_property("agents", "strategy_param_1")
        self.add_agent_property("agents", "strategy_param_2")
        self.add_agent_property("agents", "strategy_param_3")
        self.add_agent_property("agents", "share_rock")
        self.add_agent_property("agents", "share_paper")
        self.add_agent_property("agents", "share_scissors")
        self.add_environment_property("total_accumulated_payoff")

    def utility(self, agent: RPSAgent) -> float:
        """
        Defines the fitness function for the genetic algorithm.

        The trainer will aim to maximize this value. In this model, the fitness
        is simply the agent's total accumulated payoff at the end of a simulation run.
        """
        return agent.accumulated_payoff

