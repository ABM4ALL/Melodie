
from typing import ClassVar
from .config import NewConfig
from .calibrator_manager import CalibratorManager
from .model import Model

def run_calibrator(config: 'NewConfig',
                   calibrator_manager_class=ClassVar[CalibratorManager],
                   model_class=Model):
    pass
