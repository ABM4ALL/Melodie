import sys

sys.path.append("../..")
from model.scenario import AspirationScenario
from model.model import AspirationModel
from model.trainer import AspirationTrainer
from config import config
from model.dataframe_loader import AspirationDataFrameLoader

if __name__ == "__main__":
    trainer = AspirationTrainer(config=config,
                                scenario_cls=AspirationScenario,
                                model_cls=AspirationModel,
                                df_loader_cls=AspirationDataFrameLoader)
    import cProfile, pstats

    profiler = cProfile.Profile()
    profiler.enable()
    try:
        trainer.train()
    except KeyboardInterrupt:
        pass
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('tottime')
    stats.print_stats()
