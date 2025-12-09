"""
Main entry point for the grid-based CovidContagion example.

This script sets up the Melodie configuration and launches the simulator.
It uses the grid-enabled Model, Scenario, and other core components.
"""
import os
from Melodie import Config, Simulator
from core.model import CovidModel
from core.scenario import CovidScenario


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
