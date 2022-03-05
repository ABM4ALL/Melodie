import sqlalchemy

from Melodie import DataFrameLoader
from .scenario import GiniScenario


class GiniDataframeLoader(DataFrameLoader):

    def register_scenario_dataframe(self):
        scenarios_dict = {}
        self.load_dataframe('simulator_scenarios', 'simulator_scenarios.xlsx', scenarios_dict)

    def register_generated_dataframes(self):

        with self.new_table_generator('agent_params', lambda scenario: scenario.agent_num) as g:
            def generator_func(scenario: GiniScenario):
                return {
                    'id': g.increment(),
                    'productivity': scenario.agent_productivity,
                    'account': 0.0
                }
            g.set_row_generator(generator_func)
            g.set_column_data_types({
                'id': sqlalchemy.Integer(),
                'productivity': sqlalchemy.Float(),
                'account': sqlalchemy.Float()
            })
