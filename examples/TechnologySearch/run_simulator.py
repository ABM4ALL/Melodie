import sys

sys.path.append("../..")
from Melodie import Simulator, run_profile
from model.scenario import TechnologySearchScenario
from model.model import TechnologySearchModel
from config import config
from model.dataframe_loader import TechnologySearchDataFrameLoader

if __name__ == "__main__":
    simulator = Simulator(config=config,
                          scenario_cls=TechnologySearchScenario,
                          model_cls=TechnologySearchModel,
                          df_loader_cls=TechnologySearchDataFrameLoader)

    run_profile(simulator.run)
