# -*- coding:utf-8 -*-
# @Time: 2022/12/14 22:29
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: demo.py.py

from typing import TYPE_CHECKING

from Melodie import DataCollector

if TYPE_CHECKING:
    from source.scenario import AMETSScenario
    from source.environment import AMETSEnvironment


class AMETSDataCollector(DataCollector):
    scenario: "AMETSScenario"

    def setup(self):
        self.add_agent_property("agents", "id_sector")
        self.add_agent_property("agents", "id_sector_agent")
        self.add_agent_property("agents", "daily_production")
        self.add_agent_property("agents", "unit_emission")
        self.add_agent_property("agents", "emission_flow")
        self.add_agent_property("agents", "emission_stock")
        self.add_agent_property("agents", "allowance")
        self.add_agent_property("agents", "expected_total_emission")
        self.add_agent_property("agents", "expected_allowance_gap")
        self.add_agent_property("agents", "expected_allowance_gap_percent")
        self.add_agent_property("agents", "fundamental_forecast")
        self.add_agent_property("agents", "technical_forecast")
        self.add_agent_property("agents", "forecast")
        self.add_agent_property("agents", "trading_price_benchmark")
        self.add_agent_property("agents", "adopt_prob")
        self.add_agent_property("agents", "saving_option_investment_cost")
        self.add_agent_property("agents", "production_profit")
        self.add_agent_property("agents", "fine")
        self.add_agent_property("agents", "cash")
        self.add_environment_property("open")
        self.add_environment_property("high")
        self.add_environment_property("low")
        self.add_environment_property("mean")
        self.add_environment_property("close")
        self.add_environment_property("volume")
        self.add_environment_property("average_price")
        self.add_environment_property("total_volume")
        self.add_environment_property("total_adoptions")
        self.add_environment_property("abatement_ratio")
        self.add_environment_property("total_final_profit")

    @DataCollector.calc_time
    def save_transaction_history(self, environment: "AMETSEnvironment"):
        if self.status:
            transaction_history_df = environment.order_book.get_transaction_history_df()
            transaction_history_df.insert(0, "id_scenario", self.scenario.id)
            self.db.write_dataframe("transaction_history", transaction_history_df)

    @DataCollector.calc_time
    def save_price_volume_history(self, environment: "AMETSEnvironment"):
        if self.status:
            price_volume_history = []
            for period in range(0, self.scenario.period_num):
                for tick in range(0, self.scenario.tick_num):
                    price_volume_history.append(
                        {
                            "period": period,
                            "tick": tick,
                            "price": environment.order_book.price_history[period][tick],
                            "volume": environment.order_book.volume_history[period][
                                tick
                            ],
                        }
                    )
            price_volume_history_df = pd.DataFrame(price_volume_history)
            price_volume_history_df.insert(0, "id_scenario", self.scenario.id)
            self.db.write_dataframe("price_volume_history", price_volume_history_df)

    @DataCollector.calc_time
    def save_saving_option_adoptions(self, environment: "AMETSEnvironment"):
        if self.status:
            adoptions = environment.get_saving_option_adoption_df()
            adoptions.insert(0, "id_scenario", self.scenario.id)
            self.db.write_dataframe("saving_option_adoptions", adoptions)
