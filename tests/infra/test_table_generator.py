# -*- coding:utf-8 -*-
import os
import pandas as pd

from Melodie import (
    Simulator,
    Scenario,
    create_db_conn,
    Model,
    DataLoader,
    DataFrameInfo,
    Config
)

cfg_for_temp = Config(
    "temp_db_created",
    os.path.dirname(__file__),
    input_folder=os.path.join(os.path.dirname(__file__), "resources", "excels"),
    output_folder=os.path.join(os.path.dirname(__file__), "resources", "output"),
    data_output_type="sqlite"
)

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
    with simulator.data_loader.dataframe_generator(
        DataFrameInfo(df_name="aaa", columns={}), 100
    ) as g:
        g.set_row_generator(lambda scenario: {"id": g.increment(), "productivity": 0.5})

    with simulator.data_loader.dataframe_generator(
        DataFrameInfo(df_name="bbb", columns={}), lambda _: 200
    ) as g:

        def f(s):
            o = obj1()
            o.id = g.increment()
            o.productivity = 0.5
            return o

        g.set_row_generator(f)
    create_db_conn(cfg_for_temp).write_dataframe("aaa", simulator.data_loader.registered_dataframes['aaa'])
    create_db_conn(cfg_for_temp).write_dataframe("bbb", simulator.data_loader.registered_dataframes['bbb'])
    df = create_db_conn(cfg_for_temp).read_dataframe("aaa")
    print(df)
    df = create_db_conn(cfg_for_temp).read_dataframe("bbb")
    print(df)
    df = simulator.data_loader.registered_dataframes["bbb"]
    print(df)
