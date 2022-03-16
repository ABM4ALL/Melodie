from Melodie import Simulator
from .visualizer import GiniVisualizer


class GiniSimulator(Simulator):
    def setup(self):
        self.visualizer = GiniVisualizer()
        self.visualizer.setup()
