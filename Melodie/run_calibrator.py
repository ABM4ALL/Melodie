
from typing import ClassVar
from .config import NewConfig
from .calibrator_manager import Calibrator
from .model import Model

def run_calibrator(config: 'NewConfig',
                   calibrator_manager_class=ClassVar[Calibrator],
                   model_class=Model):
    pass
