from mesa import Agent


class CovidAgent(Agent):
    """
    An agent representing a person in the COVID-19 contagion model.
    """

    def __init__(self, model, health_state: int = 0):
        super().__init__(model)
        # Health state: 0 = susceptible, 1 = infected, 2 = recovered.
        self.health_state: int = health_state

    def step(self) -> None:
        """
        If infected, the agent has a chance to infect a randomly chosen agent
        in the population.
        """
        if self.health_state != 1:
            return

        other_agent = self.random.choice(self.model.agents)
        if (
            other_agent.health_state == 0
            and self.random.random() < self.model.infection_prob
        ):
            other_agent.health_state = 1
