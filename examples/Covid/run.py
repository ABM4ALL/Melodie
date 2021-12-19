import sys

sys.path.append("../..")
from model.agent import CovidAgent
from model.environment import CovidEnvironment
from model.scenario import CovidScenario
from model.data_collector import CovidDataCollector
from model.model import CovidModel
from model.simulator import CovidSimulator
from config import config

if __name__ == "__main__":

    simulator = CovidSimulator()

    """
    Run the model with simulator
    """
    simulator.run(
        config=config,
        scenario_class=CovidScenario,
        model_class=CovidModel,
    )

    """
    Run the model with simulator in parallel mode. 
    Use "cores" to determine how many cores should be used.
    """
    # simulator.run_parallel(
    #     config=config,
    #     scenario_class=CovidScenario,
    #     model_class=CovidModel,
    #     cores=4
    # )