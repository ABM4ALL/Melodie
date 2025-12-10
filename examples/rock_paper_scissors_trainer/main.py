import os
import sys

# -------------------------------------------------------------------------
# IMPORT PATH HACK FOR PARALLEL WORKERS
# -------------------------------------------------------------------------
# The Trainer uses multiprocessing. To ensure that worker processes can
# correctly import the 'examples' package to load model and scenario
# classes, the project's root directory is added to Python's path.
# This is a common pattern for running nested example modules directly
# from a repository without requiring an editable installation.
# -------------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from Melodie import Config, Simulator

from examples.rock_paper_scissors_trainer.core.model import RPSModel
from examples.rock_paper_scissors_trainer.core.scenario import RPSScenario
from examples.rock_paper_scissors_trainer.core.trainer import RPSTrainer


def get_config() -> Config:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return Config(
        project_name="RockPaperScissorsTrainer",
        project_root=base_dir,
        input_folder=os.path.join(base_dir, "data", "input"),
        output_folder=os.path.join(base_dir, "data", "output"),
    )


def run_simulator(cfg: Config) -> None:
    simulator = Simulator(config=cfg, model_cls=RPSModel, scenario_cls=RPSScenario)
    simulator.run()


def run_trainer(cfg: Config) -> None:
    # The `parallel_mode` parameter controls the parallelization strategy:
    #   - "process" (default): Uses subprocess-based parallelism. Works on all
    #     Python versions. Recommended for most use cases.
    #   - "thread": Uses thread-based parallelism. Recommended for Python 3.13+
    #     (free-threaded/No-GIL builds) for potentially faster performance by
    #     avoiding process creation overhead.
    trainer = RPSTrainer(
        config=cfg,
        scenario_cls=RPSScenario,
        model_cls=RPSModel,
        processors=4,
        parallel_mode="process",  # or "thread" for Python 3.13+
    )
    trainer.run()


if __name__ == "__main__":
    config = get_config()

    # The trainer will clear the output folder before running.
    # To see the simulator's output, run it separately.
    # run_simulator(config)

    run_trainer(config)

