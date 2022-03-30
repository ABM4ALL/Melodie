from model.scenario import ShellingModelScenario
from model.model import ShellingModelModel
from model.simulator import ShellingModelSimulator
from model.dataframe_loader import ShellingModelDataframeLoader
from config import config

if __name__ == "__main__":
    simulator = ShellingModelSimulator(
        # df_loader_cls=ShellingModelDataframeLoader,
        config=config,
        scenario_cls=ShellingModelScenario,
        model_cls=ShellingModelModel)

    """
    Run the model
    """
    simulator.run()
