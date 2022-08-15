from Melodie import Trainer
from .agent import RPSAgent


class RPSTrainer(Trainer):
    def setup(self):
        self.add_environment_property("agents_total_payoff")

        self.add_agent_training_property(
            "agent_list",
            ["strategy_param_1", "strategy_param_2", "strategy_param_3"],
            ["rock_count", "paper_count", "scissors_count", "total_payoff"],
            lambda scenario: list(range(scenario.agent_num)),
        )

        self.save_env_trainer_result = True
        self.save_agent_trainer_result = True

    def target_function(self, agent: RPSAgent):
        return -agent.total_payoff
