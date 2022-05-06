from model.scenario import GiniScenario
from model.model import GiniModel
from model.dataframe_loader import GiniDataframeLoader
from model.simulator import GiniSimulator
from config import config

if __name__ == "__main__":
    simulator = GiniSimulator(config=config,
                              scenario_cls=GiniScenario,
                              model_cls=GiniModel,
                              df_loader_cls=GiniDataframeLoader)

    simulator.run_parallel(2)
