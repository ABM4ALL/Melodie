from source.scenario import StockScenario
from source.model import StockModel
from source.calibrator import StockCalibrator
from config import config
from source.data_loader import StockDataLoader

if __name__ == "__main__":
    calibrator = StockCalibrator(
        config=config,
        model_cls=StockModel,
        scenario_cls=StockScenario,
        data_loader_cls=StockDataLoader
    )
    calibrator.calibrate()  # 可以叫main
