import sqlalchemy

from Melodie import DataFrameLoader
from .scenario import GiniScenario


class GiniDataframeLoader(DataFrameLoader):

    def register_scenario_dataframe(self):
        scenarios_dict = {}
        self.load_dataframe('simulator_scenarios', 'scenarios.xlsx', scenarios_dict)

    def register_static_dataframes(self):
        pass
        # 由于已经写进了scenario表中，所以这里不需要任何注册操作了

    def register_generated_dataframes(self):
        """

        :return:
        """
        # 使用了一个上下文管理器，在with中方便地管理表的生成。

        with self.new_table_generator('agent_params', lambda scenario: scenario.agent_num) as g:
            # 生成器。
            # 对于每一个scenario, 生成scenario.agent_num行数据。
            def generator_func(scenario: GiniScenario):
                return {'id': g.increment(), 'productivity': scenario.agent_productivity, 'account': 0.0}

            g.set_row_generator(generator_func)
            g.set_column_data_types({'productivity': sqlalchemy.Float()})
