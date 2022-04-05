from Melodie import GridVisualizer


class ShellingVisualizer(GridVisualizer):
    def setup(self):
        self.add_visualize_component('grid', 'grid', {})
        self.add_agent_series('grid', 0, 'scatter', '#ff0000')
        self.add_agent_series('grid', 1, 'scatter', '#00ff00')
        pass
