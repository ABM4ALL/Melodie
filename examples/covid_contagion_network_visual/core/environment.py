from Melodie import Environment
from typing import TYPE_CHECKING
import random

if TYPE_CHECKING:
    from Melodie import AgentList
    from .agent import CovidAgent
    from .scenario import CovidScenario


class CovidEnvironment(Environment):
    """
    Environment handles infection/recovery logic on the network structure.
    """

    scenario: "CovidScenario"

    def setup(self):
        """
        Initialize macro-level statistical counters.
        """
        self.num_susceptible = 0
        self.num_infected = 0
        self.num_recovered = 0

    def seed_infection(self, agents: "AgentList[CovidAgent]"):
        """
        Initial seeding of infection among agents.
        """
        for agent in agents:
            agent.seed_infection(self.scenario.initial_infected_percentage)

    def spread_on_network(self, agents: "AgentList[CovidAgent]"):
        """
        Network-based infection logic:
        1. Iterate through all infected agents.
        2. Find their neighbors in the network.
        3. If a neighbor is susceptible, infect them with probability `infection_prob`.
        """
        newly_infected = []
        for agent in agents:
            # Only infected agents can spread the virus
            if agent.health_state != 1:
                continue
            
            # Get neighbors from the network structure
            neighbors = self.model.network.get_neighbors(agent)
            
            for category, neighbor_id in neighbors:
                # Retrieve the actual agent object using category and ID
                neighbor = self.model.network.agent_categories[category].get_agent(neighbor_id)
                
                # Infect susceptible neighbors
                if neighbor.health_state == 0:
                    if random.random() < self.scenario.infection_prob:
                        newly_infected.append(neighbor)
        
        # Update states after iterating to avoid chain reactions in a single step
        for agent in newly_infected:
            agent.health_state = 1

    def recover(self, agents: "AgentList[CovidAgent]"):
        """
        Infected agents recover with a certain probability.
        """
        for agent in agents:
            if agent.health_state == 1 and random.random() < self.scenario.recovery_prob:
                agent.health_state = 2

    def update_population_stats(self, agents: "AgentList[CovidAgent]"):
        """
        Update statistical counts for the current step.
        """
        self.num_susceptible = 0
        self.num_infected = 0
        self.num_recovered = 0
        for agent in agents:
            if agent.health_state == 0:
                self.num_susceptible += 1
            elif agent.health_state == 1:
                self.num_infected += 1
            else:
                self.num_recovered += 1
