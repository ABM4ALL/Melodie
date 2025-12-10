from typing import Dict, Any

import pandas as pd
from mesa import Model
from mesa.datacollection import DataCollector

from .agent import CovidAgent


class CovidModel(Model):
    """
    The main model for the COVID-19 contagion simulation, implemented in Mesa.
    
    This implementation adapts to Mesa 3.0+ patterns:
    - Instead of a Scheduler, we manually manage the agent list and shuffle it each step.
    - Model parameters are unpacked from the scenario dictionary.
    """

    def __init__(self, **params: Dict[str, Any]):
        super().__init__()
        # Pass scenario parameters to the model.
        self.agent_num: int = int(params.get("agent_num", 0))
        self.initial_infected_percentage: float = float(
            params.get("initial_infected_percentage", 0.0)
        )
        self.infection_prob: float = float(params.get("infection_prob", 0.0))
        self.recovery_prob: float = float(params.get("recovery_prob", 0.0))
        self.period_num: int = int(params.get("period_num", 0))
        self.scenario_id: int = int(params.get("id", 0))

        # Create agent population; agents register themselves to model.agents
        self._create_agents()

        # The DataCollector records model-level and agent-level variables.
        self.datacollector = DataCollector(
            model_reporters={
                "num_susceptible": lambda m: m.count_health_state(0),
                "num_infected": lambda m: m.count_health_state(1),
                "num_recovered": lambda m: m.count_health_state(2),
            },
            agent_reporters={"health_state": "health_state"},
        )
    def _create_agents(self) -> None:
        """Initializes the agent population."""
        for _ in range(self.agent_num):
            # Set initial infection status based on a random draw.
            is_infected = self.random.random() < self.initial_infected_percentage
            CovidAgent(model=self, health_state=1 if is_infected else 0)

    def step(self) -> None:
        """
        Executes one time step of the simulation.
        It proceeds in three phases: infection, recovery, and data collection.
        """
        # 1. Agents interact and spread the virus.
        agent_list = list(self.agents)
        self.random.shuffle(agent_list)
        for agent in agent_list:
            agent.step()
        # 2. Infected agents have a chance to recover.
        self._recover_agents()
        # 3. Record data for this step.
        self.datacollector.collect(self)

    def run_model(self) -> None:
        """Runs the model for a fixed number of periods."""
        for _ in range(self.period_num):
            self.step()

    def _recover_agents(self) -> None:
        """Handles the recovery process for all agents."""
        for agent in self.agents:
            if agent.health_state == 1 and self.random.random() < self.recovery_prob:
                agent.health_state = 2

    def count_health_state(self, state: int) -> int:
        """Helper method to count agents in a specific health state."""
        return sum(1 for agent in self.agents if agent.health_state == state)

    @staticmethod
    def format_agent_df(
        df: pd.DataFrame, scenario_id: int, run_id: int
    ) -> pd.DataFrame:
        """
        Formats the agent-level dataframe from the DataCollector to match the
        structure expected for cross-framework comparison.
        """
        out = df.reset_index().rename(columns={"Step": "period", "AgentID": "agent_id"})
        out["scenario_id"] = scenario_id
        out["run_id"] = run_id
        return out[["scenario_id", "run_id", "period", "agent_id", "health_state"]]

    @staticmethod
    def format_model_df(
        df: pd.DataFrame, scenario_id: int, run_id: int
    ) -> pd.DataFrame:
        """
        Formats the model-level dataframe from the DataCollector to match the
        structure expected for cross-framework comparison.
        """
        out = df.reset_index().rename(columns={"index": "period"})
        out["scenario_id"] = scenario_id
        out["run_id"] = run_id
        return out[
            [
                "scenario_id",
                "run_id",
                "period",
                "num_susceptible",
                "num_infected",
                "num_recovered",
            ]
        ]
