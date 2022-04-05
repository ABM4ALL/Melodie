from .calibrator import CovidCalibrator, CovidModel, CovidScenario
from .config import cfg_for_calibrator


def test_calibrator():
    calibrator = CovidCalibrator(cfg_for_calibrator, CovidScenario, CovidModel, None)
    calibrator.calibrate()
    pass
