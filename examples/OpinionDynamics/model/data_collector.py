from Melodie import DataCollector


class OpinionDynamicsDataCollector(DataCollector):
    def setup(self):
        self.add_agent_property("agent_list", "opinion_level")
        self.add_agent_property("agent_list", "opinion_radius")
        self.add_agent_property("agent_list", "communication_action")
        self.add_agent_property("agent_list", "communication_neighbor_id")
        self.add_agent_property("agent_list", "communication_result")
        self.add_environment_property("average_opinion_level")
