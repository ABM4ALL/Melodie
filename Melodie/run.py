"""
This file stores the run function for model running, storing global variables and other services.
"""
from typing import ClassVar, TYPE_CHECKING, Optional
import logging

logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    from .environment import Environment
    from .model import Model
    from .scenariomanager import ScenarioManager, Scenario
else:
    from .model import Model
    from .scenariomanager import ScenarioManager

_model: Optional['Model'] = None


def get_environment() -> 'Environment':
    """
    get environment from the global variable
    :return:
    """
    global _model
    return _model.environment


def current_scenario() -> 'Scenario':
    """
    Get current scenario.
    :return:
    """
    return _model.scenario


def run(environment_class: ClassVar['Environment'],
        data_collector_class: ClassVar['DataCollector'] = None,
        model_class: ClassVar['Model'] = None, scenario_manager_class: ClassVar['ScenarioManager'] = None):
    """
    Main Model for running model!
    """
    global _model
    if model_class is None:
        model_class = Model
    if scenario_manager_class is None:
        scenario_manager = None
    else:
        scenario_manager: 'ScenarioManager' = scenario_manager_class()
        print(scenario_manager.to_dataframe().to_csv('x.csv', ))
    # scenario_manager.gen_scenarios()
    if scenario_manager is None:
        _model = model_class(environment_class, data_collector_class)
        _model._setup()
        _model.run()
    else:
        for scenario in scenario_manager._scenarios:
            _model = model_class(environment_class, data_collector_class, scenario)
            _model._setup()
            _model.run()
