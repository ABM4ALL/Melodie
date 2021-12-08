# -*- coding:utf-8 -*-
# @Time: 2021/12/7 20:59
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_table_generator.py
import pandas as pd

from Melodie import Simulator, Scenario, create_db_conn
from .config import cfg_for_temp


class TestSimulator(Simulator):

    def register_static_dataframes(self) -> None:
        self.registered_dataframes["scenarios"] = pd.DataFrame([
            {"id": 1, "periods": 1, 'agent_num': 100}
        ])

    def register_scenario_dataframe(self) -> None:
        pass


class obj1():
    pass


class TestScenario(Scenario):
    def setup(self):
        self.agent_num = 0


def test_table_generator():
    simulator = TestSimulator()
    simulator.config = cfg_for_temp
    simulator.register_static_dataframes()
    simulator.scenario_class = TestScenario
    print(simulator.registered_dataframes)
    with simulator.new_table_generator('aaa', 100) as g:
        g.set_row_generator(lambda scenario: {"id": g.increment(), "productivity": 0.5})
    with simulator.new_table_generator('bbb', lambda _: 200) as g:
        def f(s):
            o = obj1()
            o.id = g.increment()
            o.productivity = 0.5
            return o

        g.set_row_generator(f)
    df = create_db_conn(cfg_for_temp).read_dataframe('aaa')
    print(df)
    df = create_db_conn(cfg_for_temp).read_dataframe('bbb')
    print(df)
    df = simulator.registered_dataframes['bbb']
    print(df)
