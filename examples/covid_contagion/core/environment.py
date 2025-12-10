import random
from typing import TYPE_CHECKING

from Melodie import Environment
from .agent import CovidAgent
from .scenario import CovidScenario

if TYPE_CHECKING:
    from Melodie import AgentList


class CovidEnvironment(Environment):
    scenario: "CovidScenario"

    def setup(self) -> None:
        # Macro-level counters for population statistics.
        # These are updated each period by `update_population_stats` and recorded by the DataCollector.
        self.num_susceptible: int = 0
        self.num_infected: int = 0
        self.num_recovered: int = 0

    def setup_infection(self, agents: "AgentList[CovidAgent]") -> None:
        # Sets the initial percentage of infected agents based on scenario parameters.
        for agent in agents:
            if (
                agent.health_state == 0
                and random.random() < self.scenario.initial_infected_percentage
            ):
                agent.health_state = 1

    def agents_interaction(self, agents: "AgentList[CovidAgent]") -> None:
        # Simulates random interactions where infected agents can spread the virus.
        for agent in agents:
            if agent.health_state == 1:
                # Randomly meet another agent
                # Note: Melodie's AgentList.random_sample returns a list
                other_agent = agents.random_sample(1)[0]
                if other_agent.health_state == 0:
                    if random.random() < self.scenario.infection_prob:
                        other_agent.health_state = 1
    
    def agents_recover(self, agents: "AgentList[CovidAgent]") -> None:
        # Triggers the recovery process for all infected agents.
        for agent in agents:
            agent.health_state_update(self.scenario.recovery_prob)

    def update_population_stats(self, agents: "AgentList[CovidAgent]") -> None:
        # Aggregates agent states into environment-level population counts.
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
