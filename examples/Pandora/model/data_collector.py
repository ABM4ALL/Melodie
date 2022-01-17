
from Melodie import DataCollector

class PandoraDataCollector(DataCollector):

    def setup(self):

        self.add_agent_property("agent_list", 'x_pos')
        self.add_agent_property("agent_list", 'y_pos')
        self.add_agent_property("agent_list", 'condition')

        self.add_environment_property('accumulated_infection')
