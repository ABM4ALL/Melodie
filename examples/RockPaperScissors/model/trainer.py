from Melodie import Trainer, GeneticAlgorithmTrainer
from .agent import RPSAgent


class RPSTrainer(Trainer):
    def setup(self):
        self.container_name = "agent_list"
        self.add_agent_training_property("agent_list", "strategy_param_1")
        self.add_agent_training_property("agent_list", "strategy_param_2")
        self.add_agent_training_property("agent_list", "strategy_param_3")

        self.add_agent_result_property("agent_list", "rock_count")
        self.add_agent_result_property("agent_list", "paper_count")
        self.add_agent_result_property("agent_list", "scissors_count")
        self.add_agent_result_property("agent_list", "total_payoff")
        self.add_environment_result_property("agents_total_payoff")

        self.save_env_trainer_result = True
        self.save_agent_trainer_result = True
        self.algorithm_cls = GeneticAlgorithmTrainer

    def fitness_agent(self, agent: RPSAgent):
        return agent.total_payoff
