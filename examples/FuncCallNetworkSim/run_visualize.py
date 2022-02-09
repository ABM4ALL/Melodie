import sys

from Melodie import DataCollector

sys.path.append("../..")
# Melody package is not available on pip yet, so this example has to import Melody package placed at project root.
# Appending project root to "sys.path" makes Melody package accessible to the interpreter.
# This code will be removed as soon as we release the first distribution onto pip.
from model.agent import FuncAgent
from model.environment import FuncEnvironment
from model.scenario import FuncScenario
from model.model import FuncModel
from model.simulator import FuncSimulator
from model.visualizer import FuncCallSimVisualizer
from config import config

if __name__ == "__main__":
    simulator = FuncSimulator()

    """
    Run the model with dataframe_loader
    """
    simulator.run_visual(
        agent_class=FuncAgent,
        environment_class=FuncEnvironment,
        config=config,
        model_class=FuncModel,
        scenario_cls=FuncScenario,
        data_collector_class=DataCollector,
        visualizer_class=FuncCallSimVisualizer
    )
