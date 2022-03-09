import sys

sys.path.append("../..")
from Melodie import Simulator, run_profile
from model.scenario import RPSScenario
from model.model import RPSModel
from config import config
from model.dataframe_loader import RPSDataFrameLoader

if __name__ == "__main__":
    simulator = Simulator(config=config,
                          scenario_cls=RPSScenario,
                          model_cls=RPSModel,
                          df_loader_cls=RPSDataFrameLoader)

    run_profile(simulator.run)
