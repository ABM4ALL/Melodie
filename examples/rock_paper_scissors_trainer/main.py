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
        parallel_mode="thread",  # or "thread" for Python 3.13+
    )
    trainer.run()


if __name__ == "__main__":
    config = get_config()

    # The trainer will clear the output folder before running.
    # To see the simulator's output, run it separately.
    # run_simulator(config)

    run_trainer(config)
