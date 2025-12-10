"""
Main entry point for the grid-based CovidContagion example.

This script sets up the Melodie configuration and launches the simulator.
It uses the grid-enabled Model, Scenario, and other core components.
"""
import os
import sys
from Melodie import Config, Simulator
# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from examples.covid_contagion_grid.core.model import CovidModel
from examples.covid_contagion_grid.core.scenario import CovidScenario


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Configure project paths
    config = Config(
        project_name="CovidContagionGrid",
        project_root=base_dir,
        input_folder=os.path.join(base_dir, "data", "input"),
        output_folder=os.path.join(base_dir, "data", "output"),
    )

    # Initialize simulator with model and scenario classes
    simulator = Simulator(
        config=config,
        model_cls=CovidModel,
        scenario_cls=CovidScenario,
    )

    # Run the simulation
    simulator.run()
