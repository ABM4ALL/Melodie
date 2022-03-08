
from Melodie import DataCollector


class RPSDataCollector(DataCollector):

    def setup(self):
        self.add_agent_property("agent_list", 'period_competitor_id')
        self.add_agent_property("agent_list", 'period_action')
        self.add_agent_property("agent_list", 'period_payoff')
        self.add_agent_property("agent_list", 'total_payoff')
        self.add_agent_property("agent_list", 'rock_count')
        self.add_agent_property("agent_list", 'paper_count')
        self.add_agent_property("agent_list", 'scissors_count')
        self.add_environment_property('agents_total_payoff')


