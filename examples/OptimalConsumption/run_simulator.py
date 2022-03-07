import sys

sys.path.append("../..")
from Melodie import Simulator, run_profile
from model.scenario import OptimalConsumptionScenario
from model.model import OptimalConsumptionModel
from config import config
from model.dataframe_loader import OptimalConsumptionDataFrameLoader

if __name__ == "__main__":
    simulator = Simulator(config=config,
                          scenario_cls=OptimalConsumptionScenario,
                          model_cls=OptimalConsumptionModel,
                          df_loader_cls=OptimalConsumptionDataFrameLoader)

    run_profile(simulator.run)
