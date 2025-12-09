from typing import TYPE_CHECKING

from Melodie import Model

from examples.rock_paper_scissors_trainer.core.agent import RPSAgent
from examples.rock_paper_scissors_trainer.core.data_collector import RPSDataCollector
from examples.rock_paper_scissors_trainer.core.environment import RPSEnvironment
from examples.rock_paper_scissors_trainer.core.scenario import RPSScenario

if TYPE_CHECKING:
    from Melodie import AgentList


class RPSModel(Model):
    """
    The main model class for the Rock-Paper-Scissors simulation.

    It sets up the agents, environment, and data collector, and defines the
    main simulation loop that runs for a specified number of periods.
    """

    scenario: "RPSScenario"
    data_collector: RPSDataCollector

    def create(self) -> None:
        self.agents: "AgentList[RPSAgent]" = self.create_agent_list(RPSAgent)
        self.environment: RPSEnvironment = self.create_environment(RPSEnvironment)
        self.data_collector = self.create_data_collector(RPSDataCollector)

    def setup(self) -> None:
        # Populates the agent list using the dynamically generated parameter table
        # from the scenario.
        self.agents.setup_agents(
            agents_num=self.scenario.agent_num,
            params_df=self.scenario.agent_params,
        )

    def run(self) -> None:
        """Executes the main simulation loop for `scenario.period_num` periods."""
        for period in range(self.scenario.period_num):
            self.environment.agents_setup_data(self.agents)
            self.environment.run_game_rounds(self.agents)
            self.environment.agents_calc_action_share(period, self.agents)
            self.data_collector.collect(period)
        self.data_collector.save()

