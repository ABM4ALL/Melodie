import sys

from Melodie import Simulator, run_profile

sys.path.append("../..")
from model.scenario import CovidScenario
from model.covid_model import CovidModel
from model.dataframe_loader import CovidDataFrameLoader
from config import config

if __name__ == "__main__":

    simulator = Simulator(
        config=config,
        scenario_cls=CovidScenario,
        model_cls=CovidModel,
        df_loader_cls=CovidDataFrameLoader,
    )

    simulator.run()
