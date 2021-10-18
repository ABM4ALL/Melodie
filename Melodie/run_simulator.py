
from typing import ClassVar
from .config import NewConfig
from .simulator_manager import Simulator
from .model import Model

def run_simulator(config: 'NewConfig',
                  simulator_manager_class=ClassVar[Simulator],
                  model_class=Model):
    pass
