import pytest

from Melodie import DataLoader
from .calibrator import CovidCalibrator, CovidModel, CovidScenario
from .config import cfg_for_calibrator


class DFLoader(DataLoader):
    pass


@pytest.mark.timeout(15)
def test_calibrator():
    calibrator = CovidCalibrator(
        cfg_for_calibrator, CovidScenario, CovidModel, DFLoader
    )
    calibrator.calibrate()
