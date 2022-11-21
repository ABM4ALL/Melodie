from Melodie import Model
from .data_collector import _ALIAS_DataCollector
from .environment import _ALIAS_Environment


class _ALIAS_Model(Model):
    def setup(self):
        with self.define_basic_components():
            self.data_collector = _ALIAS_DataCollector()
            self.environment = _ALIAS_Environment()

    def run(self):
        for t in range(0, self.scenario.period_num):
            self.data_collector.collect(t)
        self.data_collector.save()
