# -*- coding:utf-8 -*-
# @Time: 2021/9/26 14:23
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_file_io.py
import os

from Melodie.basic.exceptions import MelodieException, assert_exc_occurs
from Melodie.basic.fileio import load_excel, batch_load_tables

j = lambda file_name: os.path.join(os.path.dirname(__file__), 'resources', 'excels', file_name)


def test_load_excel_same_agent_params():
    ret = load_excel(j('only_scenarios_right.xlsx'))
    assert_exc_occurs(1208, lambda: load_excel(j('only_scenarios_wrong_1208.xlsx')))
    assert_exc_occurs(1209, lambda: load_excel(j('only_scenarios_wrong_1209.xlsx')))


def test_load_excel_agent_params_variate():
    scenarios, agent_params = load_excel(j('agent_param_for_each_scenario_right.xlsx'))
    # print(agent_params)
    assert_exc_occurs(1210, lambda: load_excel(j('agent_param_for_each_scenario_wrong_1210.xlsx')))

    assert_exc_occurs(1202, lambda: load_excel(j('agent_param_for_each_scenario_wrong_1202_1.xlsx')))
    assert_exc_occurs(1202, lambda: load_excel(j('agent_param_for_each_scenario_wrong_1202_2.xlsx')))
    assert_exc_occurs(1209, lambda: load_excel(j('agent_param_for_each_scenario_wrong_1209.xlsx')))


def test_batch_load_tables():
    tables = batch_load_tables([
        j('batch_load_table_right_1.xlsx'),
        j('batch_load_table_right_2.xlsx')
    ], {'scenarios', '1', '2', '3', 'agent_params'})
    assert 'weather' in tables.keys()
    assert 'sunshine' in tables.keys()

    assert_exc_occurs(1501,
                      lambda: batch_load_tables([
                          j('batch_load_table_right_1.xlsx'),
                          j('batch_load_table_wrong_1501.xlsx')
                      ], {'scenarios', '1', '2', '3', 'agent_params'}))
