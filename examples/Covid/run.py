import sys

sys.path.append("../..")
from model.scenario import CovidScenario
from model.model import CovidModel
from model.simulator import CovidSimulator
from model.df_loader import CovidDataFrameLoader
from config import config

if __name__ == "__main__":
    simulator = CovidSimulator(
        config=config,
        scenario_cls=CovidScenario,
        model_cls=CovidModel,
        df_loader_cls=CovidDataFrameLoader)

    """
    Run the model with dataframe_loader
    """
    simulator.run()

    """
    Run the model with dataframe_loader in parallel mode. 
    Use "cores" to determine how many cores should be used.
    """
    # dataframe_loader.run_parallel(
    #     config=config,
    #     scenario_cls=CovidScenario,
    #     model_class=CovidModel,
    #     cores=4
    # )
