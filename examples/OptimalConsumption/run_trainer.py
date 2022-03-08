import sys

sys.path.append("../..")
from model.scenario import OCScenario
from model.model import OCModel
from model.trainer import OCTrainer
from config import config
from model.dataframe_loader import OCDataFrameLoader
from Melodie import run_profile

if __name__ == "__main__":
    trainer = OCTrainer(config=config,
                        scenario_cls=OCScenario,
                        model_cls=OCModel,
                        df_loader_cls=OCDataFrameLoader)
    run_profile(trainer.train)
