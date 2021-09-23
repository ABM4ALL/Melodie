# -*- coding:utf-8 -*-
# @Time: 2021/9/19 10:38
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_db.py
import os

from Melodie.db import DB, create_db_conn
from Melodie.config import Config


# def test_create_db():
#     db = DB('test')
#     assert os.path.exists('test.sqlite')
#     db.close()
#     # os.remove('test.sqlite')
#
#     db = DB('test', conn_params={'db_path': 'resources'})
#     assert os.path.exists('resources/test.sqlite')
#     db.close()
#     # os.remove('resources/test.sqlite')


def test_get_scenarios():
    scenarios = create_db_conn(
        Config('test', db_folder='resources/db', output_folder='resources/_output')).query("select * from scenarios;")

    assert scenarios.shape[0] == 3
    scenario_2 = create_db_conn(
        Config('test', db_folder='resources/db', output_folder='resources/_output')).query_scenarios(id=2)
    assert scenario_2['id'][0] == 2


def test_get_agent_results():
    cfg = Config('test', db_folder='resources/db', output_folder='resources/_output')
    agents_df = create_db_conn(cfg).query_agent_results(scenario_id=0, id=1)
    assert agents_df.shape[0] == 200
    agents_df = create_db_conn(cfg).query_agent_results(scenario_id=0, step=1)
    assert agents_df.shape[0] == 100


def test_get_env_results():
    cfg = Config('test', db_folder='resources/db', output_folder='resources/_output')
    env_df = create_db_conn(cfg).query_env_results()
    assert env_df.shape[0] == 600
    env_df = create_db_conn(cfg).query_env_results(scenario_id=0)
    assert env_df.shape[0] == 200
    print(env_df)
    env_df = create_db_conn(cfg).query_env_results(scenario_id=0, step=1)
    assert env_df.shape[0] == 1
    assert env_df['step'][0] == 1

    # scenario_2 = create_db_conn(
    #     Config('test', db_folder='resources/db', output_folder='resources/_output')).query_scenarios(id=2)
    # assert scenario_2['id'][0] == 2
