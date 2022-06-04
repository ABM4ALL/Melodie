from Melodie import Simulator

from model.scenario import OpinionDynamicsScenario
from model.model import OpinionDynamicsModel
from model.dataframe_loader import OpinionDynamicsDataframeLoader
from config import config

if __name__ == "__main__":
    simulator = Simulator(
        config=config,
        scenario_cls=OpinionDynamicsScenario,
        model_cls=OpinionDynamicsModel,
        df_loader_cls=OpinionDynamicsDataframeLoader,
    )

    simulator.run()
