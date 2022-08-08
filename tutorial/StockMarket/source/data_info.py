import sqlalchemy

from Melodie import DataFrameInfo

simulator_scenarios = DataFrameInfo(
    df_name="simulator_scenarios",
    file_name="simulator_scenarios.xlsx",
    columns={
        "id": sqlalchemy.Integer(),
        "number_of_run": sqlalchemy.Integer(),
        "periods": sqlalchemy.Integer(),
        "period_ticks": sqlalchemy.Integer(),
        "agent_num": sqlalchemy.Integer(),
        "chartist_percentage_start": sqlalchemy.Float(),
        "chartist_memory_length": sqlalchemy.Integer(),
        "fundamentalist_price_benchmark": sqlalchemy.Integer(),
        "forecast_rule_evaluation_memory_length": sqlalchemy.Integer(),
        "switch_intensity": sqlalchemy.Float(),
        "stock_price_start": sqlalchemy.Integer(),
        "stock_trading_volume": sqlalchemy.Integer(),
        "stock_account_start": sqlalchemy.Integer(),
        "cash_account_start": sqlalchemy.Integer(),
    },
)

id_forecast_rule = DataFrameInfo(
    df_name="id_forecast_rule",
    file_name="id_forecast_rule.xlsx",
    columns={
        "id": sqlalchemy.Integer(),
        "forecast_rule": sqlalchemy.String()
    }
)

agent_params = DataFrameInfo(
    df_name="agent_params",
    columns={
        "scenario_id": sqlalchemy.Integer(),
        "id": sqlalchemy.Integer(),
        "forecast_rule_id": sqlalchemy.Integer(),
        "switch_intensity": sqlalchemy.Float(),
        "stock_account": sqlalchemy.Integer(),
        "cash_account": sqlalchemy.Integer(),
    },
)
