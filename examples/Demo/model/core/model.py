
from typing import ClassVar

from .agent import DemoAgent
from .environment import DemoEnvironment
from .data_collector import DemoDataCollector
from Melodie import NewScenario


class DemoModel:
    def __init__(self,
                 scenario: 'NewScenario',
                 agent_class: ClassVar[DemoAgent],
                 environment_class: ClassVar[DemoEnvironment],
                 data_collector_class: ClassVar[DemoDataCollector],
                 run_id_in_scenario: int = 0
                 ):
        pass


