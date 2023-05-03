import pytest

from Melodie import DataLoader
from tests.calibrator import CovidCalibrator, CovidModel, CovidScenario
from tests.infra.config import cfg_for_calibrator


class DFLoader(DataLoader):
    pass


@pytest.mark.timeout(15)
def test_calibrator():
    calibrator = CovidCalibrator(
        cfg_for_calibrator, CovidScenario, CovidModel, DFLoader
    )
    calibrator.run()
