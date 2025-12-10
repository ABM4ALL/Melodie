import os
from Melodie import Config, Simulator
from core.model import CovidModel
from core.scenario import CovidScenario

if __name__ == "__main__":
    config = Config(
        project_name="CovidContagion",
        project_root=os.path.dirname(__file__),
        input_folder=os.path.join(os.path.dirname(__file__), "data/input"),
        output_folder=os.path.join(os.path.dirname(__file__), "data/output"),
    )
    
    simulator = Simulator(
        config=config,
        model_cls=CovidModel,
        scenario_cls=CovidScenario
    )
    
    simulator.run()
