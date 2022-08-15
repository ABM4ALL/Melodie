# -*- coding:utf-8 -*-
import pandas as pd

from Melodie import Simulator, Scenario, create_db_conn, Model, DataLoader, DataFrameInfo
from .config import cfg_for_temp


class TestModel(Model):
    pass


class TestDataframeLoader(DataLoader):

    def setup(self):
        self.registered_dataframes["simulator_scenarios"] = pd.DataFrame(
            [{"id": 1, "period_num": 1, "agent_num": 100}]
        )
        # self.load_dataframe(DataFrameInfo())


class TestSimulator(Simulator):
    pass


class obj1:
    pass


class TestScenario(Scenario):
    def setup(self):
        self.agent_num = 0


def test_table_generator():
    simulator = TestSimulator(
        cfg_for_temp, TestScenario, TestModel, TestDataframeLoader
    )

    simulator.setup()
    simulator.pre_run()
    with simulator.data_loader.dataframe_generator(DataFrameInfo(df_name="aaa", columns={}), 100) as g:
        g.set_row_generator(lambda scenario: {"id": g.increment(), "productivity": 0.5})

    with simulator.data_loader.dataframe_generator(DataFrameInfo(df_name="bbb", columns={}), lambda _: 200) as g:
        def f(s):
            o = obj1()
            o.id = g.increment()
            o.productivity = 0.5
            return o

        g.set_row_generator(f)
    df = create_db_conn(cfg_for_temp).read_dataframe("aaa")
    print(df)
    df = create_db_conn(cfg_for_temp).read_dataframe("bbb")
    print(df)
    df = simulator.data_loader.registered_dataframes["bbb"]
    print(df)
