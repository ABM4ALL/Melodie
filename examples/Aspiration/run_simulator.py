import sys

sys.path.append("../..")

from model.scenario import AspirationScenario
from model.model import AspirationModel
from model.simulator import AspirationSimulator
from config import config
from model.dataframe_loader import AspirationDataFrameLoader

if __name__ == "__main__":
    simulator = AspirationSimulator(config=config,
                                    scenario_cls=AspirationScenario,
                                    model_cls=AspirationModel,
                                    df_loader_cls=AspirationDataFrameLoader)

    simulator.run()
