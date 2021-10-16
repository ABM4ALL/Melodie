from config import config
from Melodie import run
from model.core.agent import DemoAgent
from model.core.agent_manager import DemoAgentManager
from model.core.model import DemoModel
from model.core.data_collector import DemoDataCollector
from model.core.scenario import Scenario

if __name__ == "__main__":
    run(
        DemoAgent,
        DemoAgentManager,
        config,
        model_class=DemoModel,
        data_collector_class=DemoDataCollector,
        # scenario_manager_class=GiniScenarioManager,
        # table_generator_class=GiniTableGenerator, --> 去掉
        # analyzer_class=Analyzer --> 去掉
    )
