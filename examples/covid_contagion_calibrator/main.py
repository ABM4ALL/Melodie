import os
import sys
from Melodie import Config, Simulator

from examples.covid_contagion_calibrator.core.calibrator import CovidCalibrator
from examples.covid_contagion_calibrator.core.model import CovidModel
from examples.covid_contagion_calibrator.core.scenario import CovidScenario


def run_calibrator(cfg):
    if sys.version_info >= (3, 13):
        parallel_mode = "thread"
    else:
        parallel_mode = "process"

    # The `parallel_mode` parameter controls the parallelization strategy:
    #   - "process" (default): Uses subprocess-based parallelism. Works on all
    #     Python versions. Recommended for most use cases.
    #   - "thread": Uses thread-based parallelism. Recommended for Python 3.13+
    #     (free-threaded/No-GIL builds) for potentially faster performance by
    #     avoiding process creation overhead.
    calibrator = CovidCalibrator(
        config=cfg,
        model_cls=CovidModel,
        scenario_cls=CovidScenario,
        processors=8,
        parallel_mode=parallel_mode,
    )
    calibrator.run()


def run_simulator(cfg):
    simulator = Simulator(
        config=cfg,
        model_cls=CovidModel,
        scenario_cls=CovidScenario
    )
    simulator.run()


def get_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return Config(
        project_name="CovidContagionCalibrator",
        project_root=base_dir,
        input_folder=os.path.join(base_dir, "data", "input"),
        output_folder=os.path.join(base_dir, "data", "output"),
    )

if __name__ == "__main__":
    
    config = get_config()
    # run_simulator(config)
    run_calibrator(config)
