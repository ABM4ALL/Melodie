import sys

sys.path.append("../..")

from model.scenario import AspirationScenario
from model.model import AspirationModel
from model.simulator import AspirationSimulator
from config import config
from model.table_loader import AspirationDataFrameLoader

if __name__ == "__main__":
    simulator = AspirationSimulator(config=config,
                                    scenario_cls=AspirationScenario,
                                    model_cls=AspirationModel,
                                    table_loader_cls=AspirationDataFrameLoader)

    """
    Run the model with simulator
    """
    simulator.run()

    """
    Run the model with simulator in parallel mode. 
    Use "cores" to determine how many cores should be used.
    """
    # register.rst.run_parallel(
    #     config=config,
    #     scenario_class=AspirationScenario,
    #     model_class=AspirationModel,
    #     cores=4
    # )
