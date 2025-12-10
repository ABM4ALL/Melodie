import os
import sys
from Melodie import Config, Simulator

# -------------------------------------------------------------------------
# IMPORT PATH HACK FOR PARALLEL WORKERS
# -------------------------------------------------------------------------
# Calibrator uses multiprocessing. Sub-processes must be able to import 
# the 'examples' package to load model/scenario classes.
# By adding the project root (../../) to sys.path, we ensure that:
#   from examples.covid_contagion_calibrator.core...
# works correctly in both the main process and worker processes.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# -------------------------------------------------------------------------

from examples.covid_contagion_calibrator.core.calibrator import CovidCalibrator
from examples.covid_contagion_calibrator.core.model import CovidModel
from examples.covid_contagion_calibrator.core.scenario import CovidScenario


def run_calibrator(cfg):
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
        parallel_mode="process",  # or "thread" for Python 3.13+
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
