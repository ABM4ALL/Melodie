import sys

from Melodie import Simulator

sys.path.append("../..")
from model.scenario import CovidScenario
from model.model import CovidModel
from model.dataframe_loader import CovidDataFrameLoader
from config import config

if __name__ == "__main__":
    simulator = Simulator(
        config=config,
        scenario_cls=CovidScenario,
        model_cls=CovidModel,
        df_loader_cls=CovidDataFrameLoader)

    # import cProfile, pstats
    #
    # profiler = cProfile.Profile()
    # profiler.enable()
    #
    # run_profile(simulator.run)
    simulator.run()
    #
    # profiler.disable()
    # stats = pstats.Stats(profiler).sort_stats('ncalls')
    # stats.print_stats(30)
