import os
import sys

sys.path.append("../..")
# Melody package is not available on pip yet, so this example has to import Melody package placed at project root.
# Appending project root to "sys.path" makes Melody package accessible to the interpreter.
# This code will be removed as soon as we release the first distribution onto pip.
from model.agent import GINIAgent
from model.environment import GiniEnvironment
from model.scenario import GiniScenario
from model.data_collector import GiniDataCollector
from model.model import GiniModel
from model.simulator import GiniSimulator

from config import config

if __name__ == "__main__":
    simulator = GiniSimulator()

    """
    Run the model with simulator
    """
    simulator.run(
        config=config,
        scenario_class=GiniScenario,
        model_class=GiniModel,
        agent_class=GINIAgent,
        environment_class=GiniEnvironment,
        data_collector_class=GiniDataCollector,
    )

    """
    Run the model with simulator in parallel mode. 
    Use "cores" to determine how many cores should be used.
    """
    # simulator.run_parallel(
    #     config=config,
    #     scenario_class=GiniScenario,
    #     model_class=GiniModel,
    #     agent_class=GINIAgent,
    #     environment_class=GiniEnvironment,
    #     data_collector_class=GiniDataCollector,
    #     cores=4
    # )