import pytest
import random

import Melodie.basic
from Melodie import OldConfig, DB, Scenario, ScenarioManager


class TestScenario(Scenario):
    def __init__(self, id):
        super().__init__(id, 10)

    def setup(self):
        self.periods = 1
        self.productivity = random.random()


class TestScenarioManager(ScenarioManager):
    def gen_scenarios(self):
        return [TestScenario(i) for i in range(100)]


class TestScenarioManagerError1201(ScenarioManager):
    def gen_scenarios(self):
        return [TestScenario(0) for i in range(10)]


class TestScenarioManagerError1202(ScenarioManager):
    def gen_scenarios(self):
        return [TestScenario({}) for i in range(10)]


class TestScenarioManagerError1203(ScenarioManager):
    def gen_scenarios(self):
        return [TestScenario(i) for i in [None, 1, 2, 3]]


class TestScenarioManagerError1204(ScenarioManager):
    def gen_scenarios(self):
        return


class TestScenarioManagerError1205(ScenarioManager):
    def gen_scenarios(self):
        return []


class TestScenarioManagerError1206(ScenarioManager):
    def gen_scenarios(self):
        return [TestScenario(i) for i in ['a', 1, 2, 3]]


class TestScenarioManagerError1207(ScenarioManager):
    def gen_scenarios(self):
        return [{} for i in range(10)]


def test_errors():
    config = OldConfig('Untitled')
    try:
        TestScenarioManagerError1201(config)
        raise Exception
    except Melodie.basic.MelodieException as e:
        assert e.id == 1201
    try:
        TestScenarioManagerError1202(config)
        raise Exception
    except Melodie.basic.MelodieException as e:
        assert e.id == 1202

    try:
        TestScenarioManagerError1203(config)
        raise Exception
    except Melodie.basic.MelodieException as e:
        assert e.id == 1203

    try:
        TestScenarioManagerError1204(config)
        raise Exception
    except Melodie.basic.MelodieException as e:
        assert e.id == 1204

    try:
        t = TestScenarioManagerError1205(config)
        raise Exception
    except Melodie.basic.MelodieException as e:
        assert e.id == 1205

    try:
        TestScenarioManagerError1206(config)
        raise Exception
    except Melodie.basic.MelodieException as e:
        assert e.id == 1206

    try:
        TestScenarioManagerError1207(config)
        raise Exception
    except Melodie.basic.MelodieException as e:
        assert e.id == 1207

# def test_scenario():
#     tsm = TestScenarioManager()
#     df = tsm.to_dataframe()
#
#     DB('test_scenario').drop_table('test_scenario_table')
#     db = DB('test_scenario', )
#     db.write_dataframe('test_scenario_table', df)
#
#     df2 = db.read_dataframe('test_scenario_table')
#     print(df2)
