from Melodie import GridVisualizer
from .agent import ShellingModelAgentTypeA, ShellingModelAgentTypeB


class ShellingVisualizer(GridVisualizer):
    def setup(self):
        self.add_visualize_component('grid', 'grid', {})
        self.add_agent_series('grid', ShellingModelAgentTypeA.category, 'scatter', '#ff0000')
        self.add_agent_series('grid', ShellingModelAgentTypeB.category, 'scatter', '#00ff00')
