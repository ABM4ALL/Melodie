# -*- coding:utf-8 -*-
# @Time: 2021/11/12 18:51
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: visualizer.py


from Melodie.visualizer import GridVisualizer


class GameOfLifeVisualizer(GridVisualizer):
    def setup(self):
        self.add_visualize_component('grid', 'grid')
        self.add_visualize_component('grid', 'grid')
        self.add_agent_series("grid", 'sheep', 'scatter', '#bbff00', )
        self.add_agent_series("grid", 'agents', 'scatter', '#bb0000', )

        self.add_plot_chart('chart1', ["series1", "series2"])
        self.add_plot_chart('chart2', ["series_chart2"])
        # add_pie_chart("pie_chart", data_source={"series1": lambda: self.model.environment.value1,
        # "series2": lambda: self.model.environment.value2})
        self.set_chart_data_source('chart1', "series1", lambda: self.model.environment.value1)
        self.set_chart_data_source('chart1', "series2", lambda: self.model.environment.value2)
        self.set_chart_data_source('chart2', "series_chart2",
                                   lambda: self.model.environment.value2 + self.model.environment.value1)

    def parse(self, grid):
        self.parse_grid_series(grid, "grid")
