from Melodie import Simulator
from config import config
from source.data_loader import CovidNetworkDataLoader
from source.model import CovidNetworkModel
from source.scenario import CovidNetworkScenario

if __name__ == "__main__":
    simulator = Simulator(
        config=config,
        model_cls=CovidNetworkModel,
        scenario_cls=CovidNetworkScenario,
        data_loader_cls=CovidNetworkDataLoader
    )
    simulator.run()
