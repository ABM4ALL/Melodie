# -*- coding:utf-8 -*-
# @Time: 2021/9/26 14:22
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: excel_loader.py
import os
import logging
from typing import List, Tuple, Set, Dict

import pandas as pd

from Melodie.basic import MelodieExceptions

logger = logging.getLogger(__name__)
print(logger.level)


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


def load_agent_params_from_excel(scenario_df: pd.DataFrame, excel_file: pd.ExcelFile) -> pd.DataFrame:
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
    """
    Load excel

    Notice: In Python 3.6 and 3.7, pandas prefers to use xlrd rather than use openpyxl.
        If use openpyxl at version <=3.7, Python might raise several errors for float digit conversion.

    :param file_name:
    :return:
    """
    f = pd.ExcelFile(file_name)
    sheet_names: List[str] = f.sheet_names
    if 'scenarios' not in sheet_names:
        raise MelodieExceptions.Scenario.NoScenarioSheetInExcel(file_name)
    scenarios: pd.DataFrame = pd.read_excel(f, sheet_name='scenarios').dropna(axis=1, how="all")
    if 'agent_params' in sheet_names:
        agent_params_sheet_df: pd.DataFrame = pd.read_excel(f, sheet_name='agent_params').dropna(
            axis=1,
            how='all')
        return scenarios, gen_agent_params_for_all_scenario(scenarios, agent_params_sheet_df)
    else:
        agent_params_sheet_df: pd.DataFrame = load_agent_params_from_excel(scenarios, f)
        return scenarios, agent_params_sheet_df


def batch_load_tables(files: List[str], existed_table_names: Set[str]) -> Dict[str, pd.DataFrame]:
    for file in files:
        if not os.path.exists(file):
            raise FileNotFoundError(file)
    excel_files_list: List[pd.ExcelFile] = [pd.ExcelFile(file) for file in files]
    tables: Dict[str, pd.DataFrame] = {}
    for excel_file in excel_files_list:
        all_sheet_names = excel_file.sheet_names
        for table_name in all_sheet_names:
            if table_name in existed_table_names:
                raise MelodieExceptions.Data.TableNameAlreadyExists(table_name, existed_table_names)
            tables[table_name] = pd.read_excel(excel_file, table_name)
    return tables


def find_excel_file_by_sheetname(item, d: Dict[int, List[str]]):
    for k, v in d.items():
        if item in v:
            return k
    return -1


def load_params(tablenames: Dict[int, List[str]], excel_files: List[pd.ExcelFile], filenames: List[str]):
    """

    :param filenames:
    :return:
    """
    all_sheet_names = []
    param_files_index: List[int] = []
    for _, sheet_names in tablenames.items():
        all_sheet_names.extend(sheet_names)
    scenario_tables = all_sheet_names.count('scenarios')
    if scenario_tables == 0:
        raise MelodieExceptions.Scenario.NoExcelFileContainsScenario(
            {filenames[i]: tablenames for i, tablenames in tablenames.items()})

    scenario_file_index = find_excel_file_by_sheetname('scenarios', tablenames)
    scenario_excel_file = excel_files[scenario_file_index]
    scenarios: pd.DataFrame = pd.read_excel(scenario_excel_file, sheet_name='scenarios').dropna(axis=1, how="all")
    param_files_index.append(scenario_file_index)
    if 'agent_params' in all_sheet_names:
        logger.info("The excel files contain a table named \'agent_params\', meaning that agents share the same "
                    "parameter in each scenario.")
        agent_params_file_index = find_excel_file_by_sheetname('agent_params', tablenames)
        agent_params_excel_file = excel_files[agent_params_file_index]
        agent_params_sheet_df: pd.DataFrame = pd.read_excel(agent_params_excel_file,
                                                            sheet_name='agent_params').dropna(axis=1, how='all')
        param_files_index.append(agent_params_file_index)
        return scenarios, gen_agent_params_for_all_scenario(scenarios, agent_params_sheet_df), param_files_index
    else:
        logger.info("The excel files contain a table named \'agent_params\', meaning that agents share the same "
                    "parameter in each scenario.")
        param_file_id = -1
        for i in range(scenarios.shape[0]):
            scenario_id, scenario_agent_init_num = convert_scenario_id_to_builtin_type(scenarios['id'][i]), \
                                                   scenarios['agent_num'][i]
            if not isinstance(scenario_id, (int, str)):
                raise MelodieExceptions.Scenario.ScenarioIDTypeError(scenario_id)
            scenario_id = str(scenario_id)
            if param_file_id == -1:
                param_file_id = find_excel_file_by_sheetname(scenario_id, tablenames)
                if param_file_id == -1:
                    raise MelodieExceptions.Scenario.ExcelLackAgentParamsSheet(scenario_id,
                                                                               [convert_scenario_id_to_builtin_type(
                                                                                   scenarios['id'][i])
                                                                                   for i in range(scenarios.shape[0])])
            else:
                if scenario_id not in tablenames[param_file_id]:
                    raise MelodieExceptions.Scenario.ExcelLackAgentParamsSheet(scenario_id,
                                                                               [convert_scenario_id_to_builtin_type(
                                                                                   scenarios['id'][i])
                                                                                   for i in range(scenarios.shape[0])]
                                                                               )
        param_files_index.append(param_file_id)
        agent_params_sheet_df: pd.DataFrame = load_agent_params_from_excel(scenarios, excel_files[param_file_id])
        return scenarios, agent_params_sheet_df, param_files_index


def load_all_excel_file(files: List[str], existed_table_names: Set[str]) -> Tuple[
    pd.DataFrame, pd.DataFrame, Dict[str, pd.DataFrame]]:
    for file in files:
        if not os.path.exists(file):
            raise FileNotFoundError(file)
    excel_files_list: List[pd.ExcelFile] = [pd.ExcelFile(file) for file in files]
    all_tables: Dict[int, List[str]] = {i: excel_files_list[i].sheet_names for i in range(len(files))}
    scenarios, agent_params, param_file_indices = load_params(all_tables, excel_files_list, files)
    tables: Dict[str, pd.DataFrame] = {}
    for i, excel_file in enumerate(excel_files_list):
        if i in param_file_indices:  # skip files containing scenarios and agent parameters.
            continue
        all_sheet_names = excel_file.sheet_names
        for table_name in all_sheet_names:
            if table_name in existed_table_names:
                raise MelodieExceptions.Data.TableNameAlreadyExists(table_name, existed_table_names)
            tables[table_name] = pd.read_excel(excel_file, table_name)
    return scenarios, agent_params, tables
