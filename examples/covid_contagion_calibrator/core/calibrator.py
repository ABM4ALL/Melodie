import os
from typing import List

import pandas as pd
from Melodie import Calibrator

from examples.covid_contagion_calibrator.core.model import CovidModel
from examples.covid_contagion_calibrator.core.scenario import CovidScenario


class CovidCalibrator(Calibrator):
    """
    Simple calibrator that tunes `infection_prob` so the final infected ratio matches a target.
    
    In this example, the target infected ratio is hardcoded to 0.8 inside the `distance` method.
    The calibrator minimizes the squared difference between the actual infected ratio and this target.
    """

    scenario_cls: type[CovidScenario]
    model_cls: type[CovidModel]

    def setup(self) -> None:
        """
        Setup the calibrator by defining which properties to tune and which to record.
        """
        # Calibrate the `infection_prob` parameter in the scenario.
        # This tells the Genetic Algorithm (GA) to optimize this specific attribute.
        self.add_scenario_calibrating_property("infection_prob")
        
        # Record environment-level data for analysis.
        # 'num_susceptible' will be recorded in `Result_Calibrator_Environment.csv`
        # allowing us to verify the calibration result.
        self.add_environment_property("num_susceptible")

    def distance(self, model: CovidModel) -> float:
        """
        Calculates the distance (error) between the model's result and the target.
        The GA minimizes this value.
        """
        env = model.environment
        
        # Calculate the ratio of agents who were infected (including recovered)
        # 1 - (susceptible / total)
        infected_ratio = 1 - env.num_susceptible / env.scenario.agent_num
        
        # Return squared error. 
        # Target is hardcoded as 0.8 (80% infection rate).
        return (infected_ratio - 0.8) ** 2

