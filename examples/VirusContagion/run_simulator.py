import sys

from Melodie import Simulator, run_profile

sys.path.append("../..")
from model.scenario import CovidScenario
from model.model import CovidModel
from model.dataframe_loader import CovidDataFrameLoader
from config import config

if __name__ == "__main__":
    simulator = Simulator(
        config=config,
        scenario_cls=CovidScenario,
        model_cls=CovidModel,
        data_loader_cls=CovidDataFrameLoader,
    )

    run_profile(simulator.run)
