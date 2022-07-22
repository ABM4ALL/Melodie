import time

import pytest

from Melodie import DataFrameLoader
from .calibrator import CovidCalibrator, CovidModel, CovidScenario
from .config import cfg_for_calibrator


class DFLoader(DataFrameLoader):
    pass


@pytest.mark.timeout(15)
def test_calibrator():
    calibrator = CovidCalibrator(
        cfg_for_calibrator, CovidScenario, CovidModel, DFLoader
    )
    calibrator.calibrate()
    pass
