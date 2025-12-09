from typing import Any, Dict

import numpy as np
import pandas as pd
from Melodie import Scenario


class RPSScenario(Scenario):
    """
    Defines and manages scenarios for the Rock-Paper-Scissors model.

    This class handles loading all input data and, notably, dynamically
    generates the agent parameter dataframe for each scenario. This approach
    is used instead of a static input file to ensure that each simulation
    run uses a unique but reproducible set of heterogeneous agent parameters
    based on the scenario's defined bounds.
    """

    def setup(self) -> None:
        # Parameters to be populated from SimulatorScenarios.csv or TrainerScenarios.csv
        self.period_num: int = 0
        self.agent_num: int = 0
        self.payoff_win_min: float = 0.0
        self.payoff_win_max: float = 0.0
        self.payoff_lose_min: float = 0.0
        self.payoff_lose_max: float = 0.0
        self.payoff_tie: float = 0.0

    def load_data(self) -> None:
        """
        Loads all scenario tables and synthesizes the agent-level parameter table.
        """
        self.simulator_scenarios = self.load_dataframe("SimulatorScenarios.csv")
        self.trainer_scenarios = self.load_dataframe("TrainerScenarios.csv")
        self.trainer_params_scenarios = self.load_dataframe("TrainerParamsScenarios.csv")
        self.agent_params = self._generate_agent_params()

    def _generate_agent_params(self) -> pd.DataFrame:
        """
        Dynamically builds the agent parameter dataframe.

        For each agent, it generates random payoff values within the bounds
        specified by the current scenario (`self.payoff_win_min`, etc.) and
        initial random strategy parameters. Using the scenario `id` as a seed
        for the random number generator ensures that the parameter set is
        reproducible for each specific scenario.
        """
        assert self.agent_num > 0, "agent_num must be positive."
        rng = np.random.default_rng(self.id)

        def generator(agent_id: int) -> Dict[str, Any]:
            return {
                "id": agent_id,
                "id_scenario": self.id,
                "payoff_rock_win": rng.uniform(self.payoff_win_min, self.payoff_win_max),
                "payoff_rock_lose": rng.uniform(self.payoff_lose_min, self.payoff_lose_max),
                "payoff_paper_win": rng.uniform(self.payoff_win_min, self.payoff_win_max),
                "payoff_paper_lose": rng.uniform(self.payoff_lose_min, self.payoff_lose_max),
                "payoff_scissors_win": rng.uniform(self.payoff_win_min, self.payoff_win_max),
                "payoff_scissors_lose": rng.uniform(self.payoff_lose_min, self.payoff_lose_max),
                "payoff_tie": self.payoff_tie,
                "strategy_param_1": rng.uniform(0, 100),
                "strategy_param_2": rng.uniform(0, 100),
                "strategy_param_3": rng.uniform(0, 100),
            }

        return pd.DataFrame(generator(agent_id) for agent_id in range(self.agent_num))

