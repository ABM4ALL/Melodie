import sys

sys.path.append("../..")
from model.scenario import AspirationScenario
from model.model import AspirationModel
from model.trainer import AspirationTrainer
from config import config
from model.table_loader import AspirationDataFrameLoader

if __name__ == "__main__":
    trainer = AspirationTrainer(config, AspirationScenario, AspirationModel, AspirationDataFrameLoader)

    """
    Run the model with register.rst
    """
    trainer.train()
