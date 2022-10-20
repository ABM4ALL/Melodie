from typing import TYPE_CHECKING

from tutorial.CovidContagion.source.data_loader import CovidDataLoader
from tutorial.CovidNetworkContagion.source import data_info

if TYPE_CHECKING:
    pass


class CovidNetworkDataLoader(CovidDataLoader):
    def setup(self):
        self.load_dataframe(data_info.simulator_scenarios)
        self.load_dataframe(data_info.id_age_group)
        self.load_dataframe(data_info.id_health_state)
        self.generate_agent_dataframe()
