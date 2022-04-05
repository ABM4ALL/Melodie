from Melodie import Agent, GeneticAlgorithmTrainer, Scenario


class TestAgent(Agent):
    def setup(self):
        self.param_a = 0.1
        self.param_b = 0.1
        self.result_value = 0

    def step(self):
        self.result_value += self.param_a + self.param_b


def _callable_f(*args, **kw):
    agents_fitness = [0, 0, 0, 0, 1]

    return agents_fitness, {}, [{'result_value': x, 'agent_id': i, 'param_a': 0.1, 'param_b': 0.2} for i, x in
                                enumerate([0, 0, 0, 0, 1])]



