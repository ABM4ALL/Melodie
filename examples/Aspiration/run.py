import sys

sys.path.append("../..")
from model.agent import AspirationAgent
from model.environment import AspirationEnvironment
from model.scenario import AspirationScenario
from model.data_collector import AspirationDataCollector
from model.model import AspirationModel
from model.simulator import AspirationSimulator
from config import config

if __name__ == "__main__":

    simulator = AspirationSimulator()

    """
    Run the model with simulator
    """
    simulator.run(
        config=config,
        scenario_class=AspirationScenario,
        model_class=AspirationModel,
        agent_class=AspirationAgent,
        environment_class=AspirationEnvironment,
        data_collector_class=AspirationDataCollector,
    )

    """
    Run the model with simulator in parallel mode. 
    Use "cores" to determine how many cores should be used.
    """
    # simulator.run_parallel(
    #     config=config,
    #     scenario_class=AspirationScenario,
    #     model_class=AspirationModel,
    #     agent_class=AspirationAgent,
    #     environment_class=AspirationEnvironment,
    #     data_collector_class=AspirationDataCollector,
    #     cores=4
    # )
