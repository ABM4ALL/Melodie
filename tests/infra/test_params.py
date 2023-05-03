# -*- coding:utf-8 -*-
# @Time: 2022/11/9 11:14
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_params.py.py
import json

import pandas as pd

from Melodie import Scenario
from MelodieInfra.lowcode.params import IntParam, ArrayParam, ParamsManager, FloatParam


class TestScenario(Scenario):
    def setup(self):
        self.a = 123
        self.f = 455.0
        self.e123 = [1, 2]
        self.df = pd.DataFrame([[1]], columns=["a"])
        print(self.df["a"][0])


def create_index_setter_pattern(index):
    def wrapper(index):
        def setter(obj, val):
            obj.e123[index] = val

        return setter

    return wrapper(index)


def test_array_params():
    scenario = TestScenario(0)
    scenario.setup()
    p1 = IntParam(
        "0", (0, 20), lambda scenario: scenario.e123[0], create_index_setter_pattern(0)
    )
    p2 = IntParam(
        "1", (0, 20), lambda scenario: scenario.e123[0], create_index_setter_pattern(1)
    )
    ap = ArrayParam("e123", [p1, p2], "e123", "e123")

    ap.value = [5, 10]

    assert ap.value[0] == 5
    assert ap.value[1] == 10

    ap.modify_object(scenario)
    assert scenario.e123[0] == 5
    assert scenario.e123[1] == 10

    print(ap.to_json())

    pm = ParamsManager()

    pm.params.append(ap)
    pm.params.append(FloatParam("f", (0, 10000), 9))

    def set_value(obj, val):
        obj.df["a"][0] = val

    df_ap = ArrayParam(
        "df", [IntParam("aaaa", (0, 100), lambda obj: obj.df["a"][0], set_value)]
    )

    pm.params.append(df_ap)

    print("plain list", pm.to_form_model())
    print("value json", pm.to_value_json())
    ParamsManager.for_each_param(pm.params, "", lambda name, param: print(name, param))

    scenario2 = TestScenario()
    scenario2.setup()
    scenario2.e123 = [4, 5]
    ParamsManager.write_obj_attrs_to_params_list(scenario2, pm.params)
    print(json.dumps(pm.to_json(), indent=4))
    print(pm.to_value_json())


def test_param_inheritance():
    int_param = IntParam("a", (0, 200))
    scenario = TestScenario(0)
    scenario.setup()
    int_param.extract_value(scenario)

    print(int_param.value)
    value_error_occurred = False
    try:
        int_param.value = 314
    except ValueError:
        value_error_occurred = True
    if not value_error_occurred:
        raise ValueError("Value error should occur before this line!")
    int_param.value = 10
    int_param.modify_object(scenario)
    assert scenario.a == 10


def test_from_or_to_object():
    pass
