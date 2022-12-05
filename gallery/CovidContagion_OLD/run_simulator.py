import sys

sys.path.append(r"C:\Users\12957\Documents\Developing\Python\melodie")
from Melodie import Simulator
from config import config
from source.visualizer import CovidVisualizer
from source.data_loader import CovidDataLoader
from source.model import CovidModel
from source.scenario import CovidScenario

if __name__ == "__main__":
    simulator = Simulator(
        config=config,
        model_cls=CovidModel,
        scenario_cls=CovidScenario,
        data_loader_cls=CovidDataLoader,
        visualizer_cls=CovidVisualizer,
    )
    # simulator.run()
    simulator.run_visual()
