import os
from Melodie import Config, Simulator
from examples.covid_contagion.core.model import CovidModel
from examples.covid_contagion.core.scenario import CovidScenario

if __name__ == "__main__":
    config = Config(
        project_name="covid_contagion",
        project_root=os.path.dirname(os.path.abspath(__file__)),
        input_folder=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "data", "input"
        ),
        output_folder=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "data", "output"
        ),
    )

    simulator = Simulator(
        config=config,
        model_cls=CovidModel,
        scenario_cls=CovidScenario,
    )
    simulator.run()
    # simulator.run_parallel(cores=8)
    # simulator.run_parallel_multithread(cores=8)
