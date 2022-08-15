import random
from typing import List, Union

from Melodie import (
    Calibrator,
    Environment,
    Model,
    AgentList,
    GridAgent,
    Scenario,
    Grid,
    DataCollector,
)


class CovidScenario(Scenario):
    def setup(self):
        self.period_num = 1
        self.agent_num = 1000
        self.initial_infected_percentage = 0.9
        self.infection_probability = 0.0


class CovidAgent(GridAgent):
    def set_category(self):
        self.category = 0

    def setup(self):
        self.condition = 0

    def move(self, grid: "Grid"):
        self.x, self.y = grid.rand_move_agent(self, "agent_list", 1, 1)
        return


class CovidEnvironment(Environment):
    scenario: "CovidScenario"

    def setup(self):
        self.infection_probability: float = self.scenario.infection_probability
        self.accumulated_infection: int = 0

    def env_run(self, agent_list: "AgentList[CovidAgent]") -> None:
        for agent in agent_list:
            if random.random() < self.infection_probability:
                agent.condition = 1

    def count(self, agent_list: "AgentList[CovidAgent]"):
        s = 0
        for agent in agent_list:
            s += agent.condition
        self.accumulated_infection = s


class CovidModel(Model):
    scenario: "CovidScenario"

    def setup(self):
        self.agent_list: AgentList[CovidAgent] = self.create_agent_container(
            CovidAgent, 1000
        )
        self.environment = self.create_environment(CovidEnvironment)
        self.data_collector = self.create_data_collector(DataCollector)

    def run(self):
        self.environment.env_run(self.agent_list)
        self.environment.count(self.agent_list)


class CovidCalibrator(Calibrator):
    def setup(self):
        self.add_environment_calibrating_property("infection_probability")
        self.add_environment_result_property("accumulated_infection")

    def target_function(self, environment: "CovidEnvironment") -> Union[float, int]:
        print(
            "infection_rate",
            environment.accumulated_infection / environment.scenario.agent_num,
            environment.scenario.infection_probability,
        )
        return (
            environment.accumulated_infection / environment.scenario.agent_num - 0.75
        ) ** 2

    def generate_scenarios(self) -> List["Scenario"]:
        return [CovidScenario(0)]

    def get_params_scenarios(self):
        return [
            {
                "id": 0,
                "number_of_path": 1,
                "number_of_generation": 1,
                "strategy_population": 100,
                "mutation_prob": 0.02,
                "strategy_param_code_length": 10,
                "infection_probability_min": 0,
                "infection_probability_max": 1,
            }
        ]
