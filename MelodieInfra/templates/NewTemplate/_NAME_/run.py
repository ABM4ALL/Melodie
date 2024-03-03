from config import config
from model.dataframe_loader import _ALIAS_DataframeLoader
from model.model import _ALIAS_Model
from model.scenario import _ALIAS_Scenario
from model.simulator import _ALIAS_Simulator

if __name__ == "__main__":
    simulator = _ALIAS_Simulator(
        df_loader_cls=_ALIAS_DataframeLoader,
        config=config,
        scenario_cls=_ALIAS_Scenario,
        model_cls=_ALIAS_Model,
    )

    """
    Run the model
    """
    simulator.run()
