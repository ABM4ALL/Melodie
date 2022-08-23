from Melodie import Simulator, Visualizer, GridVisualizer
from config import config
from source.data_loader import CovidDataLoader
from source.model import CovidModel
from source.scenario import CovidScenario

if __name__ == "__main__":

    simulator = Simulator(
        config=config,
        model_cls=CovidModel,
        scenario_cls=CovidScenario,
        data_loader_cls=CovidDataLoader,
        visualizer_cls=GridVisualizer
    )
    # simulator.run()
    simulator.run_visual()
