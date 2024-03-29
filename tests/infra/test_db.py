# -*- coding:utf-8 -*-
import os

import pandas as pd
from pandas.api.types import is_float_dtype, is_integer_dtype
from sqlalchemy.types import Integer

from Melodie import Scenario
from MelodieInfra import DBConn, MelodieException, db_conn
from tests.infra.config import cfg

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
    with db_conn(cfg) as conn:
        conn.write_dataframe("simulator_scenarios", df, if_exists="replace")


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
    data_with_types = db.execute("select * from df_with_dtypes").fetchall()
    print(data_with_types)
    assert isinstance(data_with_types[0][1], int)
    db.close()
    os.remove("test_db.sqlite")
