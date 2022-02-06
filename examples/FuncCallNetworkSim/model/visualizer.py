# -*- coding:utf-8 -*-
# @Time: 2021/11/13 18:16
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: run_studio.py
from Melodie.visualizer import NetworkVisualizer


class FuncCallSimVisualizer(NetworkVisualizer):
    def setup(self):
        self.chart_options['title']['text'] = "Function Call Graph"
        self.add_plot_chart('chart1', ["series1", "series2"])
