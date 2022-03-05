
import random
import numpy as np

from Melodie import Agent
from .scenario import GiniScenario


class GiniAgent(Agent):
    scenario: GiniScenario

    def setup(self):
        self.account = .0
        self.productivity = .0

    def go_produce(self):
        rand = random.random()
        if rand <= self.productivity:
            self.account += 1
        else:
            pass

        return None



class PandoraAgent(Agent):

    def setup(self):
        self.political_interest = 0
        self.technology_interest = 0
        self.house_owner = 1
        self.environmental_attitude = 0
        self.political_attitude = 0
        self.expectancy_fairness = 0.0
        self.expectancy_financial_burden = 0.0
        self.expectancy_effectiveness = 0.0
        self.attitude_vector = np.zeros(3)  # Vector contains the Output of the policy evaluation (ExV)
        self.has_attitude = False

    def process_policy_info(self, policy_info_a):
        self.has_attitude = True
        if not self._should_use_deliberative_process():
            self._use_spontaneous_process()
        else:
            self._use_deliberative_process(policy_info_a)

    def _should_use_deliberative_process(self):
        use_deliberative_process = False
        if self.political_interest > 0 or self.technology_interest > 0 or self.house_owner:
            use_deliberative_process = True
        else:
            pass
        return use_deliberative_process

    def _use_spontaneous_process(self):
        pass

    def _use_deliberative_process(self, policy_info_b):
        input_vector = self._construct_evaluation_input(policy_info_b)
        value_vector = self._evaluate(input_vector)
        expectancy_vector = self._construct_expectancy()
        self.attitude_vector = expectancy_vector * value_vector # Element wise product of the vectors 'expectancy' and 'value'

    def _construct_evaluation_input(self, policy_info_c):
        influencing_properties = np.zeros(2)
        influencing_properties[0] = self.environmental_attitude
        influencing_properties[1] = self.political_attitude

        return np.concatenate([policy_info_c, influencing_properties])

    def _evaluate(self, input_vector):
        return np.dot(input_vector, self.model.regression_coefficients)

    def _construct_expectancy(self):
        expectancy_properties = np.zeros(3)
        expectancy_properties[0] = self.expectancy_fairness
        expectancy_properties[1] = self.expectancy_financial_burden
        expectancy_properties[2] = self.expectancy_effectiveness

        return expectancy_properties

    def get_attitude_vector(self):
        return self.attitude_vector

    def _receive_message(self, sender_attitude):
        self.has_attitude = True
        value_vector = sender_attitude
        expectancy_vector = self._construct_expectancy()
        self.attitude_vector = expectancy_vector * value_vector

    def step(self):
        if self.has_attitude:
            other_agent = self
            while other_agent == self:
                other_agent = self.random.choice(self.model.schedule.agents)

            other_agent._receive_message(self.attitude_vector)
            print(self.unique_id, 'sent to', other_agent.unique_id)


