import sys

sys.path.append("../..")
from Melodie import Simulator

from model.scenario import CovidScenario
from model.covid_model import CovidModel
from model.data_loader import CovidDataLoader
from config import config

if __name__ == "__main__":

    simulator = Simulator(
        config=config,
        scenario_cls=CovidScenario,
        model_cls=CovidModel,
        df_loader_cls=CovidDataLoader,
    )  # 顺序：config, model_cls, scenario_cls, dataframe_loader_cls

    simulator.run()
