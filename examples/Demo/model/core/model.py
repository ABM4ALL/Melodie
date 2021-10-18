from typing import ClassVar

from .agent import DemoAgent
from .environment import DemoEnvironment
from .data_collector import DemoDataCollector
from Melodie import NewScenario, current_scenario


class DemoModel:
    def __init__(self,
                 # scenario: 'NewScenario',
                 agent_class: ClassVar[DemoAgent],
                 environment_class: ClassVar[DemoEnvironment],
                 data_collector_class: ClassVar[DemoDataCollector],
                 run_id_in_scenario: int = 0
                 ):
        scenario = current_scenario()

        # 在这里，通过scenario来初始化agent_list、environment等。
        # model可以不通过全局变量，而是通过传入的scenario来访问静态数据、agent的初始参数等。
        # calibrator调用Model的时候，和simulator有何不同？
        # 二者和model互动时，都是提供一组scenario。通过不同的方式组装scenario。
        # 但是二者提供下一个scenario的方式不一样。
        # scenario暂定为通过全局变量传递。
