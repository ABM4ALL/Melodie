import sys

sys.path.append("../..")
from model.scenario import CovidScenario
from model.model import CovidModel
from model.simulator import CovidSimulator
from model.table_loader import CovidDataFrameLoader
from config import config

if __name__ == "__main__":
    simulator = CovidSimulator(
        config=config,
        scenario_cls=CovidScenario,
        model_cls=CovidModel,
        table_loader_cls=CovidDataFrameLoader)

    """
    Run the model with register.rst
    """
    simulator.run()

    """
    Run the model with register.rst in parallel mode. 
    Use "cores" to determine how many cores should be used.
    """
    # register.rst.run_parallel(
    #     config=config,
    #     scenario_class=CovidScenario,
    #     model_class=CovidModel,
    #     cores=4
    # )
