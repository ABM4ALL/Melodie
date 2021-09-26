# -*- coding:utf-8 -*-
# @Time: 2021/9/26 14:23
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_file_io.py
from Melodie.basic.exceptions import MelodieException, assert_exc_occurs
from Melodie.basic.fileio import load_excel


def test_load_excel_same_agent_params():
    ret = load_excel('resources/excels/only_scenarios_right.xlsx')
    # print(ret)
    assert_exc_occurs(1208, lambda: load_excel('resources/excels/only_scenarios_wrong_1208.xlsx'))
    assert_exc_occurs(1209, lambda:
    load_excel('resources/excels/only_scenarios_wrong_1209.xlsx'))


def test_load_excel_agent_params_variate():
    scenarios, agent_params = load_excel('resources/excels/agent_param_for_each_scenario_right.xlsx')
    print(agent_params)
    assert_exc_occurs(1210, lambda: load_excel('resources/excels/agent_param_for_each_scenario_wrong_1210.xlsx'))

    assert_exc_occurs(1202, lambda: load_excel('resources/excels/agent_param_for_each_scenario_wrong_1202_1.xlsx'))
    assert_exc_occurs(1202, lambda: load_excel('resources/excels/agent_param_for_each_scenario_wrong_1202_2.xlsx'))
    assert_exc_occurs(1209, lambda: load_excel('resources/excels/agent_param_for_each_scenario_wrong_1209.xlsx'))
