import sys

sys.path.append("../..")
from Melodie import Simulator
from model.scenario import AspirationScenario
from model.model import AspirationModel
from config import config
from model.dataframe_loader import AspirationDataFrameLoader

if __name__ == "__main__":
    simulator = Simulator(config=config,
                          scenario_cls=AspirationScenario,
                          model_cls=AspirationModel,
                          df_loader_cls=AspirationDataFrameLoader)

    simulator.run()
