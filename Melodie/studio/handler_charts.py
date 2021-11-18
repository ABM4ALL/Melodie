# -*- coding:utf-8 -*-
# @Time: 2021/11/16 10:53
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: handler_charts.py
import json
import os.path

from flask import Blueprint, request
from .file_manager import JSONManager
from .messages import Response
from .config_manager import get_config_manager

charts = Blueprint('charts', __name__)


@charts.route('getChartPolicies')
def chart_policies():
    chart_type: str = request.args.get("chartType")
    policies, err = JSONManager.from_file(get_config_manager().basic_config.CHART_POLICIES_FILE, dict)
    if err is not None:
        return Response.error(err)
    if chart_type not in policies.keys():
        return Response.error(f"chart type {chart_type} not found!")
    else:
        return Response.ok(policies[chart_type])


@charts.route('chartOptions')
def chart_option():
    chart_name = request.args.get("chartName")
    options, err = JSONManager.from_file(get_config_manager().basic_config.CHART_STYLE_CONFIG_FILE, dict)
    if err is not None:
        return Response.error(err)
    chart_options = options.get(chart_name)
    if chart_options is None:
        return Response.error(f"chart option for '{chart_name}' not defined")
    else:
        return Response.ok(chart_options)


@charts.route('deleteChartOptions', methods=["post"])
def delete_chart_options():
    options, err = JSONManager.from_file(get_config_manager().basic_config.CHART_STYLE_CONFIG_FILE, dict)
    if err is not None:
        return Response.error(err)
    data = json.loads(request.data)
    chart_name = data.get("chartName")
    if options.get(chart_name) is None:
        return Response.error(f"chart {chart_name} options not saved")
    else:
        options.pop(chart_name)
        err = JSONManager.to_file(options, get_config_manager().basic_config.CHART_STYLE_CONFIG_FILE)
        if err is not None:
            return Response.error(err)
        else:
            return Response.ok("ok")


@charts.route('setChartOptions', methods=["post"])
def set_chart_option():
    style_config_file = get_config_manager().basic_config.CHART_STYLE_CONFIG_FILE
    if os.path.exists(style_config_file):
        options, err = JSONManager.from_file(style_config_file, dict)
        if err is not None:
            return Response.error(err)
    else:
        options = {}
    data = json.loads(request.data)
    chart_name = data.get("chartName")
    chart_options = data.get("chartOptions")
    assert chart_name is not None
    options[chart_name] = chart_options
    err = JSONManager.to_file(options, style_config_file)
    if err is not None:
        return Response.error(err)
    else:
        return Response.ok("msg")
