"""
Entry point for the CovidContagionNetwork example.
Usage: python main.py
"""
import os
import sys
from Melodie import Config, Simulator
# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from examples.covid_contagion_network.core.model import CovidModel
from examples.covid_contagion_network.core.scenario import CovidScenario


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config = Config(
        project_name="CovidContagionNetwork",
        project_root=base_dir,
        input_folder=os.path.join(base_dir, "data", "input"),
        output_folder=os.path.join(base_dir, "data", "output"),
    )

    simulator = Simulator(
        config=config,
        model_cls=CovidModel,
        scenario_cls=CovidScenario,
    )
    simulator.run()

