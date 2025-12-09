"""Visualizer runner - called by MelodieStudio."""
import os
from Melodie import Config, Simulator
from core.model import CovidModel
from core.scenario import CovidScenario
from core.visualizer import CovidVisualizer

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

