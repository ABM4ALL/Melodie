import sys

sys.path.append("../..")
from model.scenario import OptimalConsumptionScenario
from model.model import OptimalConsumptionModel
from model.trainer import OptimalConsumptionTrainer
from config import config
from model.dataframe_loader import OptimalConsumptionDataFrameLoader
from Melodie import run_profile

if __name__ == "__main__":
    trainer = OptimalConsumptionTrainer(config=config,
                                        scenario_cls=OptimalConsumptionScenario,
                                        model_cls=OptimalConsumptionModel,
                                        df_loader_cls=OptimalConsumptionDataFrameLoader)
    run_profile(trainer.train)
