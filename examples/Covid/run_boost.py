import logging
import os
import sys

sys.path.append("../..")
# Melody package is not available on pip yet, so this example has to import Melody package placed at project root.
# Appending project root to "sys.path" makes Melody package accessible to the interpreter.
# This code will be removed as soon as we release the first distribution onto pip.
from model.agent import CovidAgent
from model.environment import CovidEnvironment
from model.scenario import CovidScenario
from model.model import CovidModel
from model.simulator import CovidSimulator
from model.df_loader import CovidDataFrameLoader
from config import config

logger = logging.getLogger(__name__)

from Melodie.boost.compiler.typeinferlib import register_type
from Melodie.boost.compiler.class_compiler import add_custom_jit_class

register_type(list, 'List')
register_type(CovidAgent)
# register_type(Strategy1)
# register_type(Strategy2)

# register_type(Strategy)
# add_custom_jit_class(Strategy)

# add_custom_jit_class(Strategy1)
# add_custom_jit_class(Strategy2)
logging.basicConfig(level=logging.INFO)
if __name__ == "__main__":
    simulator = CovidSimulator(config, CovidScenario, CovidModel, CovidDataFrameLoader)

    """
    Run the model with register.rst
    """
    simulator.run_boost(
        [CovidAgent],
        CovidEnvironment,
        config,
        model_class=CovidModel,
        scenario_cls=CovidScenario,
        boost_model_class=CovidModel,
        model_components=None,
    )
