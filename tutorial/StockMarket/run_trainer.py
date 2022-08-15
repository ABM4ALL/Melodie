from source.scenario import StockScenario
from source.model import StockModel
from source.trainer import StockTrainer
from config import config
from source.data_loader import StockDataLoader

if __name__ == "__main__":
    trainer = StockTrainer(
        config=config,
        model_cls=StockModel,
        scenario_cls=StockScenario,
        data_loader_cls=StockDataLoader,
        processors=4,  # 啥意思，默认值是多少？
    )
    trainer.run()
