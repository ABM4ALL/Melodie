
from Melodie import run_calibrator
from .config import config
from .model.core.model import DemoModel
from .calibrator.calibrator import DemoCalibrator

if __name__ == "__main__":
    run_calibrator(config,
                   calibrator_manager_class=DemoCalibrator,
                   model_class=DemoModel,
    )
