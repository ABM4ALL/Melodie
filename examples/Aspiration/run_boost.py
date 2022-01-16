import sys

from examples.Aspiration.model.aspiration_update_strategy import AspirationUpdateStrategy
from examples.Aspiration.model.market_strategy import MarketStrategy
from examples.Aspiration.model.technology_search_strategy import TechnologySearchStrategy, \
    SleepTechnologySearchStrategy, ExploitationTechnologySearchStrategy, ExplorationTechnologySearchStrategy, \
    ImitationTechnologySearchStrategy

sys.path.append("../..")
from model.agent import AspirationAgent
from model.environment import AspirationEnvironment
from model.scenario import AspirationScenario
from model.data_collector import AspirationDataCollector
from model.model import AspirationModel
from model.simulator import AspirationSimulator
from config import config
from Melodie.boost.compiler.compiler import add_globals
from Melodie.boost.compiler.class_compiler import add_custom_jit_class, add_dtype_map
from Melodie.boost.compiler.typeinferlib import register_type

if __name__ == "__main__":
    add_globals({AspirationAgent.__name__: AspirationAgent, AspirationEnvironment.__name__: AspirationEnvironment})
    add_dtype_map(AspirationEnvironment, "np.ndarray")
    register_type(MarketStrategy)
    register_type(AspirationAgent)
    register_type(AspirationEnvironment)
    register_type(AspirationUpdateStrategy)
    register_type(TechnologySearchStrategy)
    add_custom_jit_class(SleepTechnologySearchStrategy)
    add_custom_jit_class(ExplorationTechnologySearchStrategy)
    add_custom_jit_class(ExploitationTechnologySearchStrategy)
    add_custom_jit_class(ImitationTechnologySearchStrategy)
    simulator = AspirationSimulator()

    """
    Run the model with register.rst
    """
    simulator.run_boost(
        config=config,
        scenario_class=AspirationScenario,
        model_class=AspirationModel,
        agent_class=AspirationAgent,
        environment_class=AspirationEnvironment,
        data_collector_class=AspirationDataCollector,
    )
