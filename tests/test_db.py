# -*- coding:utf-8 -*-
import os

import pandas as pd
from pandas.api.types import is_integer_dtype, is_float_dtype
from sqlalchemy.types import Integer

from MelodieInfra import create_db_conn, DBConn
from Melodie import Scenario
from Melodie.utils import MelodieException
from .config import cfg

cfg = cfg


def test_init_database():
    scenarios = [Scenario(i) for i in range(3)]
    df = pd.DataFrame(
        [
            {
                "id": scenario.id,
                "run_num": scenario.run_num,
                "period_num": scenario.period_num,
            }
            for scenario in scenarios
        ]
    )
    print(df)
    create_db_conn(cfg).write_dataframe("simulator_scenarios", df, if_exists="replace")


def test_sqlalchemy_data_types():
    """
    In-memory sqlite testcase.
    :return:
    """
    # engine = create_engine('sqlite://', echo=False)
    db = DBConn("test_db")
    db.register_dtypes("df_with_dtypes", {"A": Integer(), "B": Integer()})
    df = pd.DataFrame({"A": [1, None, 2], "B": [1, 3, 2]})

    db.write_dataframe("df_default_dtypes", df)
    try:
        db.read_dataframe("unexisted_table")
        assert False, "Code should raise exception above"
    except MelodieException as e:
        assert e.id == 1503  # Assert error 1503 occurs
    got_df = db.read_dataframe("df_default_dtypes")

    # As column `A` contains a None value, it will be converted to float64 with a NaN.
    # At the same time `B` is still integer.
    assert is_float_dtype(got_df.dtypes["A"])
    assert is_integer_dtype(got_df.dtypes["B"])

    # db.write_dataframe('df_with_dtypes', df, data_types={'A': Integer(), 'B': Integer()})
    db.write_dataframe("df_with_dtypes", df)
    # df.to_sql('df_with_dtypes', engine, index=False, dtype={'A': Integer(), 'B': Integer()})
    data_with_types = db.get_engine().execute("select * from df_with_dtypes").fetchall()
    print(data_with_types)
    assert isinstance(data_with_types[0][1], int)
    db.close()
    os.remove("test_db.sqlite")

# def test_get_scenarios():
#     scenarios = create_db_conn(cfg).query("select * from simulator_scenarios;")
#
#     assert scenarios.shape[0] == 3
#     scenario_2 = create_db_conn(cfg).query_scenarios(id=2)
#     assert scenario_2["id"][0] == 2

#
# def test_get_agent_results():
#     agents_df = create_db_conn(cfg).query_agent_results(
#         "agent", id_scenario=0, agent_id=1
#     )
#     assert agents_df.shape[0] == 200
#     agents_df = create_db_conn(cfg).query_agent_results("agent", id_scenario=0, period=1)
#     assert agents_df.shape[0] == 100


# def test_get_env_results():
#     env_df = create_db_conn(cfg).query_env_results()
#     assert env_df.shape[0] == 600
#     env_df = create_db_conn(cfg).query_env_results(id_scenario=0)
#     assert env_df.shape[0] == 200
#     print(env_df)
#     env_df = create_db_conn(cfg).query_env_results(id_scenario=0, period=1)
#     assert env_df.shape[0] == 1
#     assert env_df["period"][0] == 1

# scenario_2 = create_db_conn(
#     Config('test', db_folder='resources/db', output_folder='resources/output')).query_scenarios(id=2)
# assert scenario_2['id'][0] == 2
