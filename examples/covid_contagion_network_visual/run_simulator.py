"""Visualizer runner - called by MelodieStudio."""
import os
from Melodie import Config, Simulator

from examples.covid_contagion_network_visual.core.model import CovidModel
from examples.covid_contagion_network_visual.core.scenario import CovidScenario
from examples.covid_contagion_network_visual.core.visualizer import CovidVisualizer

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    config = Config(
        project_name="CovidContagionNetworkVisual",
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
