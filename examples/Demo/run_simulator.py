from Melodie import run_simulator
from .config import config
from .model.core.model import DemoModel
from .simulator.simulator_manager import DemoSimulatorManager

if __name__ == "__main__":
    run_simulator(config,
                  simulator_manager_class=DemoSimulatorManager,
                  model_class=DemoModel,
    )
