import pytest
import random

import Melodie.basic
from Melodie.db import DB
from Melodie.scenariomanager import Scenario, ScenarioManager


class TestScenario(Scenario):
    def setup(self):
        self.productivity = random.random()


class TestScenarioManager(ScenarioManager):
    def gen_scenarios(self):
        return [TestScenario() for i in range(100)]


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
    try:
        TestScenarioManagerError1201()
        raise Exception
    except Melodie.basic.MelodieException as e:
        assert e.id == 1201
    try:
        TestScenarioManagerError1202()
        raise Exception
    except Melodie.basic.MelodieException as e:
        assert e.id == 1202

    try:
        TestScenarioManagerError1203()
        raise Exception
    except Melodie.basic.MelodieException as e:
        assert e.id == 1203

    try:
        TestScenarioManagerError1204()
        raise Exception
    except Melodie.basic.MelodieException as e:
        assert e.id == 1204

    try:
        t = TestScenarioManagerError1205()
        raise Exception
    except Melodie.basic.MelodieException as e:
        assert e.id == 1205

    try:
        TestScenarioManagerError1206()
        raise Exception
    except Melodie.basic.MelodieException as e:
        assert e.id == 1206

    try:
        TestScenarioManagerError1207()
        raise Exception
    except Melodie.basic.MelodieException as e:
        assert e.id == 1207


def test_scenario():
    tsm = TestScenarioManager()
    df = tsm.to_dataframe()
    db = DB('test_scenario', )
    db.write_dataframe('test_scenario', df)

    df2 = db.read_table('test_scenario')
    print(df2)
