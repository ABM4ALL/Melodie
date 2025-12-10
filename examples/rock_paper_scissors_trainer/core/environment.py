import random
from typing import TYPE_CHECKING

from Melodie import AgentList, Environment

from examples.rock_paper_scissors_trainer.core.agent import RPSAgent

if TYPE_CHECKING:
    from examples.rock_paper_scissors_trainer.core.scenario import RPSScenario


class RPSEnvironment(Environment):
    """
    The environment for the Rock-Paper-Scissors model.

    It is responsible for orchestrating the agent interactions by randomly
    pairing them up for battles in each period. It also tracks the total
    accumulated payoff across all agents as a macro-level indicator.
    """

    scenario: "RPSScenario"

    def setup(self) -> None:
        """Initializes environment-level properties."""
        self.total_accumulated_payoff = 0.0

    @staticmethod
    def agents_setup_data(agents: "AgentList[RPSAgent]") -> None:
        """
        Prepares derived variables for all agents at the beginning of each period.
        """
        for agent in agents:
            agent.setup_action_prob()
            agent.setup_action_payoff()

    def run_game_rounds(self, agents: "AgentList[RPSAgent]") -> None:
        """
        In each period, randomly pairs up all agents to play one round of the game.
        """
        assert self.scenario.agent_num % 2 == 0, "scenario.agent_num must be even."
        agent_ids = list(range(self.scenario.agent_num))
        random.shuffle(agent_ids)
        for idx in range(0, len(agent_ids), 2):
            opponent_idx = idx + 1
            if opponent_idx >= len(agent_ids):
                break
            self.agents_battle(agents[agent_ids[idx]], agents[agent_ids[opponent_idx]])

    def agents_battle(self, agent_1: "RPSAgent", agent_2: "RPSAgent") -> None:
        """
        Executes a single battle between two agents, determines the outcome,
        and updates their payoffs.
        """
        agent_1.id_competitor = agent_2.id
        agent_2.id_competitor = agent_1.id

        agent_1.select_action()
        agent_2.select_action()

        if agent_1.action == agent_2.action:
            agent_1.result = agent_2.result = "tie"
        elif (
            (agent_1.action == "rock" and agent_2.action == "paper")
            or (agent_1.action == "paper" and agent_2.action == "scissors")
            or (agent_1.action == "scissors" and agent_2.action == "rock")
        ):
            agent_1.result = "lose"
            agent_2.result = "win"
        else:
            agent_1.result = "win"
            agent_2.result = "lose"

        agent_1.set_action_payoff()
        agent_2.set_action_payoff()
        self.total_accumulated_payoff += agent_1.payoff + agent_2.payoff

    def agents_calc_action_share(self, period: int, agents: "AgentList[RPSAgent]") -> None:
        """
        Triggers the calculation of action shares for all agents at the very
        end of the simulation run.
        """
        if period == self.scenario.period_num - 1:
            for agent in agents:
                agent.calc_action_percentage()

