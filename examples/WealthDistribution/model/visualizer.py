# -*- coding:utf-8 -*-
# @Time: 2021/11/12 18:51
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: visualizer.py


from Melodie import GridVisualizer


class GiniVisualizer(GridVisualizer):
    def setup(self):
        self.add_plot_chart('chart1', ["wealth"])
        self.add_plot_chart('chart2', ["gini"])

        self.set_chart_data_source('chart1', "wealth", lambda: self.model.environment.total_wealth)
        self.set_chart_data_source('chart2', "gini", lambda: self.model.environment.gini)
        # self.set_chart_data_source('chart2', "series_chart2",
        #                            lambda: self.model.environment.value2 + self.model.environment.value1)
