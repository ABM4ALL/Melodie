import sys

sys.path.append("../..")
from model.scenario import AspirationScenario
from model.model import AspirationModel
from model.trainer import AspirationTrainer
from config import config

if __name__ == "__main__":
    trainer = AspirationTrainer(config, AspirationScenario, AspirationModel)

    """
    Run the model with register.rst
    """
    trainer.train()
