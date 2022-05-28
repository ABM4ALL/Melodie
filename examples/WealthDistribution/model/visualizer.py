# -*- coding:utf-8 -*-


from Melodie import GridVisualizer


class GiniVisualizer(GridVisualizer):
    def setup(self):
        self.add_plot_chart('chart1', ["wealth"])
        self.add_plot_chart('chart2', ["gini"])

        self.set_chart_data_source('chart1', "wealth", lambda: self.model.environment.total_wealth)
        self.set_chart_data_source('chart2', "gini", lambda: self.model.environment.gini)
