import random
from typing import TYPE_CHECKING

from Melodie import Environment

if TYPE_CHECKING:
    from Melodie import AgentList
    from .agent import CovidAgent
    from .scenario import CovidScenario


class CovidEnvironment(Environment):
    """
    The environment class orchestrates the simulation steps and manages macro-level logic.
    """

    scenario: "CovidScenario"

    def setup(self) -> None:
        """
        Initialize macro-level counters for statistics.
        """
        self.num_susceptible: int = 0
        self.num_infected: int = 0
        self.num_recovered: int = 0

    def agents_move(self, agents: "AgentList[CovidAgent]") -> None:
        """
        1. Agents move.
        """
        for agent in agents:
            agent.move()

    def agents_infect(self, agents: "AgentList[CovidAgent]") -> None:
        """
        2. Infected agents spread the virus.
        """
        for agent in agents:
            agent.infect_neighbors(agents)

    def agents_recover(self, agents: "AgentList[CovidAgent]") -> None:
        """
        3. Infected agents try to recover.
        """
        for agent in agents:
            agent.recover()

    def seed_infection(self, agents: "AgentList[CovidAgent]") -> None:
        """
        Infect a percentage of agents at the start of the simulation.
        """
        for agent in agents:
            if random.random() < self.scenario.initial_infected_percentage:
                agent.health_state = 1

    def update_population_stats(self, agents: "AgentList[CovidAgent]") -> None:
        """
        Count the number of agents in each health state.
        """
        self.num_susceptible = 0
        self.num_infected = 0
        self.num_recovered = 0
        for agent in agents:
            if agent.health_state == 0:
                self.num_susceptible += 1
            elif agent.health_state == 1:
                self.num_infected += 1
            elif agent.health_state == 2:
                self.num_recovered += 1
