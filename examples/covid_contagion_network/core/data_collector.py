from Melodie import DataCollector
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Melodie import AgentList
    from .agent import CovidAgent
    from .environment import CovidEnvironment


class CovidDataCollector(DataCollector):
    """
    Collects simulation data.
    """

    environment: "CovidEnvironment"
    agents: "AgentList[CovidAgent]"

    def setup(self):
        """
        Configure data collection.
        """
        # Collect global environment properties (S-I-R counts)
        self.add_environment_property("num_susceptible")
        self.add_environment_property("num_infected")
        self.add_environment_property("num_recovered")

        # Collect agent properties
        self.add_agent_property("agents", "health_state")
