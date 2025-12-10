from typing import Dict, Any, List

import agentpy as ap
import pandas as pd


class CovidAgent(ap.Agent):
    """
    An agent representing a person in the COVID-19 contagion model.
    """

    def setup(self):
        """Initializes the agent's state."""
        # Health state: 0 = susceptible, 1 = infected, 2 = recovered.
        self.health_state: int = 0


class CovidModel(ap.Model):
    """
    The main model for the COVID-19 contagion simulation, implemented in AgentPy.
    
    This implementation manually bridges the gap between Melodie's scenario-based execution
    and AgentPy's standard flow by adding explicit setup/run control logic.
    """

    def __init__(self, parameters: Dict[str, Any]):
        super().__init__(parameters=parameters)
        # Store scenario and run IDs for data recording.
        self.scenario_id: int = int(parameters.get("id", 0))
        self.run_id: int = 0
        self._is_setup: bool = False

    def setup(self):
        """
        Initializes the model's state and components at the start of a run.
        """
        # Expose scenario parameters for easier access.
        self.period_num: int = int(self.p.get("period_num", 0))
        self.agent_num: int = int(self.p.get("agent_num", 0))
        self.initial_infected_percentage: float = float(
            self.p.get("initial_infected_percentage", 0.0)
        )
        self.infection_prob: float = float(self.p.get("infection_prob", 0.0))
        self.recovery_prob: float = float(self.p.get("recovery_prob", 0.0))

        # Create the agent population.
        self.agents: ap.AgentList = ap.AgentList(self, self.agent_num, CovidAgent)
        for agent in self.agents:
            if self.random.random() < self.initial_infected_percentage:
                agent.health_state = 1

        # Data recorders for this run (manual collection).
        self.env_records: List[Dict[str, Any]] = []
        self.agent_records: List[Dict[str, Any]] = []
        self._is_setup = True

    def step(self):
        """
        Executes one time step of the simulation.
        It proceeds in three phases: infection, recovery, and data recording.
        """
        # 1. Infection: Infected agents may spread the virus to a random other agent.
        for agent in self.agents:
            if agent.health_state == 1:
                other = self.random.choice(self.agents)
                if (
                    other.health_state == 0
                    and self.random.random() < self.infection_prob
                ):
                    other.health_state = 1

        # 2. Recovery: Infected agents have a chance to recover.
        for agent in self.agents:
            if agent.health_state == 1 and self.random.random() < self.recovery_prob:
                agent.health_state = 2

        # 3. Data recording (manual): Record macro and micro states for this period.
        period = len(self.env_records)
        counts = self._count_health_states()
        counts.update(
            {"period": period, "scenario_id": self.scenario_id, "run_id": self.run_id}
        )
        self.env_records.append(counts)
        for agent in self.agents:
            self.agent_records.append(
                {
                    "scenario_id": self.scenario_id,
                    "run_id": self.run_id,
                    "period": period,
                    "agent_id": agent.id,
                    "health_state": agent.health_state,
                }
            )

    def run_model(self):
        """Runs the model for a fixed number of periods."""
        if not self._is_setup:
            self.setup()
        for _ in range(self.period_num):
            self.step()

    def _count_health_states(self) -> Dict[str, int]:
        """Helper method to count agents in each health state."""
        return {
            "num_susceptible": sum(1 for a in self.agents if a.health_state == 0),
            "num_infected": sum(1 for a in self.agents if a.health_state == 1),
            "num_recovered": sum(1 for a in self.agents if a.health_state == 2),
        }

    def agent_dataframe(self) -> pd.DataFrame:
        """Returns the collected agent-level data as a pandas DataFrame."""
        return pd.DataFrame(self.agent_records)

    def environment_dataframe(self) -> pd.DataFrame:
        """Returns the collected model-level data as a pandas DataFrame."""
        return pd.DataFrame(self.env_records)
