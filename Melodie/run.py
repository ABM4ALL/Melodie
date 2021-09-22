"""
This file stores the run function for model running, storing global variables and other services.
"""
from typing import ClassVar, TYPE_CHECKING, Optional
import logging

from .agent import Agent
from .agent_manager import AgentManager
from .table_generator import TableGenerator

logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    from .environment import Environment
    from .model import Model
    from .scenariomanager import ScenarioManager, Scenario
    from .datacollector import DataCollector
else:
    from .model import Model
    from .scenariomanager import ScenarioManager
    # from .datacollector import DataCollector

_model: Optional['Model'] = None


def get_environment() -> 'Environment':
    """
    get environment from the global variable
    :return:
    """
    global _model
    return _model.environment


def get_agent_manager() -> 'AgentManager':
    global _model
    return _model.agent_manager


def current_scenario() -> 'Scenario':
    """
    Get current scenario.
    :return:
    """
    return _model.scenario


def get_data_collector() -> 'DataCollector':
    return _model.data_collector


def run(proj_name: str, agent_class: ClassVar['Agent'], environment_class: ClassVar['Environment'],
        data_collector_class: ClassVar['DataCollector'] = None,
        model_class: ClassVar['Model'] = None, scenario_manager_class: ClassVar['ScenarioManager'] = None,
        table_generator_class: ClassVar['TableGenerator'] = None):
    """
    Main Model for running model!
    """
    global _model
    if model_class is None:
        model_class = Model

    if scenario_manager_class is None:
        scenario_manager = None
    else:
        scenario_manager: 'ScenarioManager' = scenario_manager_class(proj_name)

    if scenario_manager is None:
        _model = model_class(proj_name, environment_class, data_collector_class, table_generator_class)
        _model._setup()
        _model.run()
    else:
        for scenario in scenario_manager._scenarios:
            _model = model_class(proj_name, agent_class, environment_class, data_collector_class, table_generator_class,
                                 scenario)
            _model._setup()
            _model.run()
