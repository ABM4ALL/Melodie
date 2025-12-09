import random
from typing import Dict, Tuple, TYPE_CHECKING

from Melodie import Agent

if TYPE_CHECKING:
    from examples.rock_paper_scissors_trainer.core.scenario import RPSScenario


class RPSAgent(Agent):
    """
    Represents an agent playing the Rock-Paper-Scissors game.

    Each agent has its own unique payoff settings for winning, losing, or tying,
    as well as three strategy parameters that determine the probabilities of
    choosing rock, paper, or scissors. These strategy parameters are the target
    for the evolutionary training by the Trainer module. The agent also tracks
    its own play history and accumulated payoffs.
    """

    scenario: "RPSScenario"

    def setup(self) -> None:
        # Payoff settings injected via agent params dataframe.
        self.payoff_rock_win: float = 0.0
        self.payoff_rock_lose: float = 0.0
        self.payoff_paper_win: float = 0.0
        self.payoff_paper_lose: float = 0.0
        self.payoff_scissors_win: float = 0.0
        self.payoff_scissors_lose: float = 0.0
        self.payoff_tie: float = 0.0

        # Strategy weights to be trained by the Trainer.
        self.strategy_param_1: float = 0.0
        self.strategy_param_2: float = 0.0
        self.strategy_param_3: float = 0.0

        self._reset_counters()

    def _reset_counters(self) -> None:
        """Initializes or resets the agent's state for a new simulation run."""
        self.id_competitor: int = 0
        self.action: str = ""
        self.result: str = ""
        self.payoff: float = 0.0
        self.accumulated_payoff: float = 0.0
        self.n_rock: int = 0
        self.n_paper: int = 0
        self.n_scissors: int = 0
        self.share_rock: float = 0.0
        self.share_paper: float = 0.0
        self.share_scissors: float = 0.0

    def setup_action_prob(self) -> None:
        """
        Normalizes the three strategy parameters into a probability distribution
        for choosing rock, paper, or scissors.
        """
        if self.strategy_param_1 == self.strategy_param_2 == self.strategy_param_3 == 0:
            # Avoid division by zero if a chromosome is all zeros during training.
            self.strategy_param_1 = self.strategy_param_2 = self.strategy_param_3 = 1.0
        total = self.strategy_param_1 + self.strategy_param_2 + self.strategy_param_3
        self.action_prob = {
            "rock": self.strategy_param_1 / total,
            "paper": self.strategy_param_2 / total,
            "scissors": self.strategy_param_3 / total,
        }

    def setup_action_payoff(self) -> None:
        """
        Creates a lookup dictionary that maps (action, outcome) pairs to their
        corresponding payoffs. This helps to keep the battle logic clean.
        """
        self.action_payoff: Dict[Tuple[str, str], float] = {
            ("rock", "win"): self.payoff_rock_win,
            ("rock", "lose"): self.payoff_rock_lose,
            ("paper", "win"): self.payoff_paper_win,
            ("paper", "lose"): self.payoff_paper_lose,
            ("scissors", "win"): self.payoff_scissors_win,
            ("scissors", "lose"): self.payoff_scissors_lose,
            ("rock", "tie"): self.payoff_tie,
            ("paper", "tie"): self.payoff_tie,
            ("scissors", "tie"): self.payoff_tie,
        }

    def select_action(self) -> None:
        """
        Selects an action (rock, paper, or scissors) based on the current
        strategy probabilities and updates the action counter.
        """
        rand = random.random()
        if rand <= self.action_prob["rock"]:
            self.action = "rock"
            self.n_rock += 1
        elif rand <= self.action_prob["rock"] + self.action_prob["paper"]:
            self.action = "paper"
            self.n_paper += 1
        else:
            self.action = "scissors"
            self.n_scissors += 1

    def set_action_payoff(self) -> None:
        """
        Records the payoff for the last action taken and adds it to the
        accumulated payoff for the current simulation run.
        """
        self.payoff = self.action_payoff[(self.action, self.result)]
        self.accumulated_payoff += self.payoff

    def calc_action_percentage(self) -> None:
        """
        Calculates the agent's long-term share of each action at the end of a
        simulation run. This is useful for analyzing the evolved strategies.
        """
        if self.scenario.period_num > 0:
            self.share_rock = self.n_rock / self.scenario.period_num
            self.share_paper = self.n_paper / self.scenario.period_num
            self.share_scissors = self.n_scissors / self.scenario.period_num

