from Melodie import Simulator
from config import config
from source.data_loader import CovidGridDataLoader
from source.model import CovidGridModel
from source.scenario import CovidGridScenario

if __name__ == "__main__":
    simulator = Simulator(
        config=config,
        model_cls=CovidGridModel,
        scenario_cls=CovidGridScenario,
        data_loader_cls=CovidGridDataLoader,
    )
    simulator.run()
