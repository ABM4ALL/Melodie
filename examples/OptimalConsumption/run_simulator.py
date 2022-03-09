import sys

sys.path.append("../..")
from Melodie import Simulator, run_profile
from model.scenario import OCScenario
from model.model import OCModel
from config import config
from model.dataframe_loader import OCDataFrameLoader

if __name__ == "__main__":
    simulator = Simulator(config=config,
                          scenario_cls=OCScenario,
                          model_cls=OCModel,
                          df_loader_cls=OCDataFrameLoader)

    run_profile(simulator.run)
