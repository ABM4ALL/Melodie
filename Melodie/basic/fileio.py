# -*- coding:utf-8 -*-
# @Time: 2021/9/26 14:22
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: excel_loader.py
from typing import List, Tuple

import pandas as pd

from Melodie.basic import MelodieExceptions


def convert_scenario_id_to_builtin_type(val):
    if isinstance(val, (int, str)):
        return val
    else:
        try:
            return val.item()
        except AttributeError:
            raise MelodieExceptions.Scenario.ScenarioIDTypeError(val)


def gen_agent_params_for_all_scenario(scenario_df: pd.DataFrame, agent_params_sheet_df: pd.DataFrame):
    agent_params_df = pd.DataFrame()
    for i in range(scenario_df.shape[0]):
        scenario_id, agent_num = convert_scenario_id_to_builtin_type(scenario_df['id'][i]), scenario_df['agent_num'][i]
        if agent_num != agent_params_sheet_df.shape[0]:
            raise MelodieExceptions.Scenario.ExcelAgentParamsRecordCountNotConsistentToScneario(
                scenario_id, agent_num, 'agent_params', agent_params_sheet_df.shape[0])
        else:
            agent_params_sheet_df['scenario_id'] = scenario_id
            agent_params_df = pd.concat([agent_params_df, agent_params_sheet_df])
    return agent_params_df


def load_agent_params_from_excel(scenario_df: int, excel_file: pd.ExcelFile):
    agent_params_df = pd.DataFrame()
    all_sheets = excel_file.sheet_names
    for i in range(scenario_df.shape[0]):
        scenario_id, scenario_agent_init_num = convert_scenario_id_to_builtin_type(scenario_df['id'][i]), \
                                               scenario_df['agent_num'][i]
        if not isinstance(scenario_id, (int, str)):
            raise MelodieExceptions.Scenario.ScenarioIDTypeError(scenario_id)
        if str(scenario_id) not in all_sheets:
            raise MelodieExceptions.Scenario.ExcelLackAgentParamsSheet(scenario_id)
        agent_params_sheet_df = excel_file.parse(str(scenario_id))
        if scenario_agent_init_num != agent_params_sheet_df.shape[0]:
            raise MelodieExceptions.Scenario.ExcelAgentParamsRecordCountNotConsistentToScneario(
                scenario_id, scenario_agent_init_num, 'agent_params', agent_params_sheet_df.shape[0])
        else:
            agent_params_sheet_df['scenario_id'] = scenario_id
            agent_params_df = pd.concat([agent_params_df, agent_params_sheet_df])
    return agent_params_df


def load_excel(file_name: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    f = pd.ExcelFile(file_name)
    sheet_names: List[str] = f.sheet_names
    if 'scenarios' not in sheet_names:
        raise MelodieExceptions.Scenario.NoScenarioSheetInExcel(file_name)
    scenarios: pd.DataFrame = pd.read_excel(file_name, sheet_name='scenarios').dropna(axis=1, how="all")
    if 'agent_params' in sheet_names:
        agent_params_sheet_df: pd.DataFrame = pd.read_excel(file_name, sheet_name='agent_params').dropna(axis=1,
                                                                                                         how='all')
        return scenarios, gen_agent_params_for_all_scenario(scenarios, agent_params_sheet_df)
    else:
        agent_params_sheet_df: pd.DataFrame = load_agent_params_from_excel(scenarios, f)
        return scenarios, agent_params_sheet_df
