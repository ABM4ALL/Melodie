from model.scenario import ShellingModelScenario
from model.model import ShellingModelModel
from model.simulator import ShellingModelSimulator
from config import config

if __name__ == "__main__":
    simulator = ShellingModelSimulator(
        config=config,
        scenario_cls=ShellingModelScenario,
        model_cls=ShellingModelModel)

    """
    Run the model
    """
    simulator.run_visual()
