import sys

sys.path.append("../..")
from model.scenario import TechnologySearchScenario
from model.model import TechnologySearchModel
from model.trainer import TechnologySearchTrainer
from config import config
from model.dataframe_loader import TechnologySearchDataFrameLoader
from Melodie import run_profile

if __name__ == "__main__":
    trainer = TechnologySearchTrainer(config=config,
                                      scenario_cls=TechnologySearchScenario,
                                      model_cls=TechnologySearchModel,
                                      df_loader_cls=TechnologySearchDataFrameLoader)
    run_profile(trainer.train)
