import sys

sys.path.append("../..")
from model.scenario import RPSScenario
from model.model import RPSModel
from model.trainer import RPSTrainer
from config import config
from model.dataframe_loader import RPSDataFrameLoader
from Melodie import run_profile

if __name__ == "__main__":
    trainer = RPSTrainer(
        config=config,
        scenario_cls=RPSScenario,
        model_cls=RPSModel,
        df_loader_cls=RPSDataFrameLoader,
    )
    run_profile(trainer.new_train)
