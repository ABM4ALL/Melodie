
from Melodie import DataCollector


class AspirationDataCollector(DataCollector):

    def setup(self):
        self.add_agent_property("agent_list", 'technology')
        self.add_agent_property("agent_list", 'aspiration_level')
        self.add_agent_property("agent_list", 'profit')
        self.add_agent_property("agent_list", 'account')
        self.add_agent_property("agent_list", 'profit_aspiration_difference')
        self.add_agent_property("agent_list", 'sleep_count')
        self.add_agent_property("agent_list", 'exploration_count')
        self.add_agent_property("agent_list", 'exploitation_count')
        self.add_agent_property("agent_list", 'imitation_count')
        self.add_agent_property("agent_list", 'be_learned_count')
        self.add_agent_property("agent_list", "prob_exploration")
        self.add_agent_property("agent_list", "prob_exploitation")

        self.add_environment_property('average_technology')
        self.add_environment_property('average_account')
