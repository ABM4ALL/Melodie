from Melodie import GridVisualizer


class CovidVisualizer(GridVisualizer):
    def setup(self):
        self.add_plot_chart("chart1", ["s0", "s1", "s2", "s3", "s4"])
        self.add_plot_chart("chart2", [], 'pie')
        self.add_plot_chart('bar1', [], 'bar')

        self.set_chart_data_source("chart1", "s0", lambda: self.model.environment.s0)
        self.set_chart_data_source("chart1", "s1", lambda: self.model.environment.s1)
        self.set_chart_data_source("chart1", "s2", lambda: self.model.environment.s2)
        self.set_chart_data_source("chart1", "s3", lambda: self.model.environment.s3)
        self.set_chart_data_source("chart1", "s4", lambda: self.model.environment.s4)

        self.set_chart_data_source("chart2", "s0", lambda: self.model.environment.s0)
        self.set_chart_data_source("chart2", "s1", lambda: self.model.environment.s1)
        self.set_chart_data_source("chart2", "s2", lambda: self.model.environment.s2)
        self.set_chart_data_source("chart2", "s3", lambda: self.model.environment.s3)
        self.set_chart_data_source("chart2", "s4", lambda: self.model.environment.s4)

        self.set_chart_data_source("bar1", "s0", lambda: self.model.environment.s0)
        self.set_chart_data_source("bar1", "s1", lambda: self.model.environment.s1)
        self.set_chart_data_source("bar1", "s2", lambda: self.model.environment.s2)
