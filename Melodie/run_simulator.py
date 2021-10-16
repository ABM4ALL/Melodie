
from typing import ClassVar
from .config import NewConfig
from .simulator_manager import SimulatorManager
from .model import Model

def run_simulator(config: 'NewConfig',
                  simulator_manager_class=ClassVar[SimulatorManager],
                  model_class=Model):
    pass
