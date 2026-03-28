import os

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
    #   - None (default): Auto-selects "thread" on Python 3.13+ and "process"
    #     on older Python versions.
    #   - "process": Uses subprocess-based parallelism and works on all
    #     Python versions.
    #   - "thread": Uses thread-based parallelism and can avoid process
    #     creation overhead.
    trainer = RPSTrainer(
        config=cfg,
        scenario_cls=RPSScenario,
        model_cls=RPSModel,
        processors=4,
        parallel_mode="thread",  # or "process"; omit to auto-select
    )
    trainer.run()


if __name__ == "__main__":
    config = get_config()

    # The trainer will clear the output folder before running.
    # To see the simulator's output, run it separately.
    # run_simulator(config)

    run_trainer(config)
