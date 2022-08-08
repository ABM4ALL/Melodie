import sys

sys.path.append("../..")
from model.scenario import CovidScenario
from model.model import CovidModel
from model.calibrator import CovidCalibrator
from config import config
from model.dataframe_loader import CovidDataFrameLoader

if __name__ == "__main__":
    calibrator = CovidCalibrator(
        config, CovidScenario, CovidModel, CovidDataFrameLoader
    )
    calibrator.run()
