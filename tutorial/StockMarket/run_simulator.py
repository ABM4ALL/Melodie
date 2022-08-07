from Melodie import Simulator
from config import config
from source.data_loader import StockDataLoader
from source.model import StockModel
from source.scenario import StockScenario

if __name__ == "__main__":

    simulator = Simulator(
        config=config,
        model_cls=StockModel,
        scenario_cls=StockScenario,
        data_loader_cls=StockDataLoader,
    )
    simulator.run()  # 可以叫main
