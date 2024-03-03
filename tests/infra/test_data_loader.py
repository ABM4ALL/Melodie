from collections import namedtuple

from sqlalchemy import BigInteger, Float

from Melodie import DataFrameInfo, DataLoader, Scenario
from tests.infra.config import cfg_dataloader_with_cache


def test_data_loader():
    sim = namedtuple("PseudoSimulator", ["data_loader"])

    loader = DataLoader(sim, cfg_dataloader_with_cache, Scenario)
    loader.clear_cache()
    loader.clear_cache()
    df_info = DataFrameInfo(
        df_name="agent_param_for_each_scenario_right",
        columns={
            "id": BigInteger(),
            "number_of_run": BigInteger(),
            "agent_num": BigInteger(),
            "periods": BigInteger(),
            "agent_account_min": BigInteger(),
            "agent_account_max": BigInteger(),
            "agent_productivity": Float(),
            "trade_num": BigInteger(),
            "rich_win_prob": Float(),
        },
        file_name="agent_param_for_each_scenario_right.xlsx",
    )
    loader.load_dataframe(df_info)

    df = loader.registered_dataframes[df_info.df_name]
    # print(df)
    assert len(df) == 3

    loader2 = DataLoader(sim, cfg_dataloader_with_cache, Scenario)
    ret = loader2.load_dataframe("agent_param_for_each_scenario_right.xlsx")
    df = loader2.registered_dataframes["agent_param_for_each_scenario_right"]
    assert id(ret) == id(df)
    assert len(df) == 3

    loader2.clear_cache()
    ret = loader2.load_dataframe("agent_param_for_each_scenario_right.xlsx")
    assert len(df) == 3
    ret = loader2.load_dataframe("agent_param_for_each_scenario_right.xlsx")
    assert len(df) == 3
