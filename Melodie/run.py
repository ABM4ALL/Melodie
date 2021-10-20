"""
This data stores the run function for model running, storing global variables and other services.
"""
import time
from typing import ClassVar, TYPE_CHECKING, Optional
import logging

from .agent import Agent
from .agent_manager import AgentManager
from .table_generator import TableGenerator

# 拆分为几个run：simulator, analyzer, calibrator

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    )
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .environment import Environment
    from .model import Model
    from .scenario_manager import ScenarioManager, Scenario
    from .data_collector import DataCollector
    from .config import Config
else:
    from .scenario_manager import ScenarioManager
    from .config import Config
    from .db import create_db_conn

_model: Optional['Model'] = None
_config: Optional['Config'] = None
_current_scenario: Optional['Scenario'] = None


def get_environment() -> 'Environment':
    """
    get environment from the global variable
    :return:
    """
    global _model
    assert _model is not None
    return _model.environment


def get_agent_manager() -> 'AgentManager':
    global _model
    assert _model is not None
    return _model.agent_manager


def current_scenario() -> 'Scenario':
    """
    Get current scenario.
    :return:
    """
    assert _current_scenario is not None
    return _current_scenario


def get_data_collector() -> 'DataCollector':
    assert _model is not None
    return _model.data_collector


def get_config() -> 'Config':
    assert _config is not None
    return _config


def set_config(config: "Config"):
    global _config
    _config = config


def get_run_id() -> int:
    global _model
    return _model.run_id_in_scenario


def run_new(config: ClassVar['Config'],  # 这个传入的应该是实例吧？
            model_class: ClassVar['Model'],
            scenario_class=None,
            analyzer_class: ClassVar['Analyzer'] = None
            ):
    """
    Main Model for running model!
    If
    """
    global _model, _config, _current_scenario
    if config is None:
        config = Config('Untitled')
        _config = config
    else:
        _config = config
        if _config.with_db:
            create_db_conn().reset()

    logger.info('Loading scenarios and static tables...')

    scenario_manager = ScenarioManager(config, scenario_class)

    if scenario_manager is None:
        _model = model_class(config, run_id_in_scenario=0)
        _model._setup()
        _model.run()
    else:

        if config.with_db:
            scenarios = scenario_manager.load_scenarios()
        else:
            scenarios = scenario_manager.gen_scenarios()

        for scenario_index, scenario in enumerate(scenarios):
            _current_scenario = scenario
            for run_id in range(scenario.number_of_run):
                logger.info(f'Running {run_id + 1} times in scenario {scenario.id}.')
                t0 = time.time()
                _model = model_class(config, run_id_in_scenario=run_id)
                t1 = time.time()
                _model.run()
                t2 = time.time()

                if analyzer_class is not None:
                    analyzer_class().run()
                t3 = time.time()

                model_setup_time = t1 - t0
                model_run_time = t2 - t1
                analyzer_run_time = t3 - t2
                if _model.data_collector is not None:
                    data_collect_time = _model.data_collector._time_elapsed
                    model_run_time -= data_collect_time
                info = (f'Running {run_id + 1} in scenario {scenario.id} completed with time elapsed(seconds):\n'
                        f'    model-setup   \t {round(model_setup_time, 6)}\n'
                        f'    model-run     \t {round(model_run_time, 6)}\n')
                if _model.data_collector is not None:
                    info += f'    data-collect  \t {round(data_collect_time, 6)}\n'
                info += f'    the analyzer  \t {round(analyzer_run_time, 6)}'
                logger.info(info)

            logger.info(f'{scenario_index + 1} of {len(scenarios)} scenarios has completed.')


def run(
        agent_class: ClassVar['Agent'],
        environment_class: ClassVar['Environment'],
        config: 'Config' = None,
        data_collector_class: ClassVar['DataCollector'] = None,
        model_class: ClassVar['Model'] = None,
        scenario_class: ClassVar['Scenario'] = None,
        scenario_manager_class: ClassVar['ScenarioManager'] = None,
        table_generator_class: ClassVar['TableGenerator'] = None,
        analyzer_class: ClassVar['Analyzer'] = None
):
    """
    Main Model for running model!
    If
    """
    from .model import Model

    global _model, _config, _current_scenario
    if config is None:
        config = Config('Untitled')
        _config = config
    else:
        _config = config
        if _config.with_db:
            create_db_conn().reset()

    if model_class is None:
        model_class = Model

    logger.info('Loading scenarios and static tables...')
    if scenario_manager_class is None:
        scenario_manager = ScenarioManager(config, scenario_class)
    else:
        scenario_manager: 'ScenarioManager' = scenario_manager_class(config, scenario_class)

    # if scenario_manager is None:
    #     _model = model_class(config,
    #                          scenario,
    #                          agent_class,  # 新加的
    #                          environment_class,
    #                          data_collector_class,
    #                          table_generator_class)
    #     _model._setup()
    #     _model.run()
    # else:
    if config.with_db:
        scenarios = scenario_manager.load_scenarios()
    else:
        scenarios = scenario_manager.gen_scenarios()
    for scenario_index, scenario in enumerate(scenarios):
        _current_scenario = scenario
        for run_id in range(scenario.number_of_run):
            logger.info(f'Running {run_id + 1} times in scenario {scenario.id}.')
            t0 = time.time()
            _model = model_class(config,
                                 scenario,
                                 agent_class,
                                 environment_class,
                                 data_collector_class,
                                 table_generator_class=table_generator_class,
                                 run_id_in_scenario=run_id)

            _model._setup()
            t1 = time.time()
            _model.run()
            t2 = time.time()

            if analyzer_class is not None:
                analyzer_class().run()
            t3 = time.time()

            model_setup_time = t1 - t0
            model_run_time = t2 - t1
            analyzer_run_time = t3 - t2
            if _model.data_collector is not None:
                data_collect_time = _model.data_collector._time_elapsed
                model_run_time -= data_collect_time
            info = (f'Running {run_id + 1} in scenario {scenario.id} completed with time elapsed(seconds):\n'
                    f'    model-setup   \t {round(model_setup_time, 6)}\n'
                    f'    model-run     \t {round(model_run_time, 6)}\n')
            if _model.data_collector is not None:
                info += f'    data-collect  \t {round(data_collect_time, 6)}\n'
            info += f'    the analyzer  \t {round(analyzer_run_time, 6)}'
            logger.info(info)

        logger.info(f'{scenario_index + 1} of {len(scenarios)} scenarios has completed.')
