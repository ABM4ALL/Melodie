"""Visualizer runner - called by MelodieStudio."""
import os
import sys
from Melodie import Config, Simulator

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from examples.covid_contagion_grid_visual.core.model import CovidModel
from examples.covid_contagion_grid_visual.core.scenario import CovidScenario
from examples.covid_contagion_grid_visual.core.visualizer import CovidVisualizer

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    config = Config(
        project_name="CovidContagionGridVisual",
        project_root=base_dir,
        input_folder=os.path.join(base_dir, "data", "input"),
        output_folder=os.path.join(base_dir, "data", "output"),
        visualizer_port=8765,
    )

    simulator = Simulator(
        config=config,
        model_cls=CovidModel,
        scenario_cls=CovidScenario,
        visualizer_cls=CovidVisualizer,
    )
    simulator.run_visual()

