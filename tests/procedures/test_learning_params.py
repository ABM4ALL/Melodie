import pandas as pd
import tests.procedures.base
from Melodie.trainer import GATrainerParams
from Melodie.calibrator import GACalibratorParams


def test_trainer_params():
    data = [
        {
            "id": 0,
            "path_num": 1,
            "generation_num": 1,
            "strategy_population": 10,
            "mutation_prob": 0.02,
            "strategy_param_code_length": 1,
            "p_max": 1,
            "p_min": 0,
        }
    ]
    gtp_1 = GATrainerParams(**data[0])
    record = pd.DataFrame(data)
    gtp_2 = GATrainerParams.from_dataframe_record(record.to_dict(orient="records")[0])
    assert hash(gtp_1) == hash(gtp_2)
    assert gtp_2.strategy_param_code_length == 1


def test_calibrator_params():
    data = [
        {
            "id": 0,
            "path_num": 1,
            "generation_num": 1,
            "strategy_population": 10,
            "mutation_prob": 0.02,
            "strategy_param_code_length": 1,
            "p_max": 1,
            "p_min": 0,
        }
    ]
    gcp_1 = GACalibratorParams(**data[0])
    record = pd.DataFrame(data)
    gcp_2 = GACalibratorParams.from_dataframe_record(
        record.to_dict(orient="records")[0]
    )
    assert hash(gcp_1) == hash(gcp_2)
    assert gcp_2.strategy_param_code_length == 1
    assert gcp_1.parameters[0].max == 1
    assert gcp_1.parameters[0].min == 0
    assert gcp_2.parameters[0].max == 1
    assert gcp_2.parameters[0].min == 0
