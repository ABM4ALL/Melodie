from typing import ClassVar

from .datacollector import DataCollector
from .environment import Environment


class Model:
    def __init__(self, environment_class: ClassVar[Environment],
                 data_collector_class: ClassVar[DataCollector] = None,
                 scenario=None):

        self.scenario = scenario
        self.environment = environment_class()

        if callable(data_collector_class) and issubclass(data_collector_class, DataCollector):
            data_collector = data_collector_class()
            data_collector.setup()
        elif data_collector_class is None:
            data_collector = None
        else:
            raise TypeError
        self.data_collector = data_collector

    def _setup(self):
        self.environment.setup()

    def run(self):
        pass
