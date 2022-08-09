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
        "fundamentalist_weight_min": sqlalchemy.Float(),
        "fundamentalist_weight_max": sqlalchemy.Float(),
        "fundamentalist_forecast_min": sqlalchemy.Float(),
        "fundamentalist_forecast_max": sqlalchemy.Float(),
        "chartist_forecast_start_min": sqlalchemy.Float(),
        "chartist_forecast_start_max": sqlalchemy.Float(),
        "chartist_forecast_memory_length": sqlalchemy.Integer(),
        "stock_price_start": sqlalchemy.Float(),
        "stock_trading_volume": sqlalchemy.Integer(),
        "stock_account_start": sqlalchemy.Integer(),
        "cash_account_start": sqlalchemy.Float(),
    },
)

agent_params = DataFrameInfo(
    df_name="agent_params",
    columns={
        "scenario_id": sqlalchemy.Integer(),
        "id": sqlalchemy.Integer(),
        "fundamentalist_weight": sqlalchemy.Integer(),
        "fundamentalist_forecast": sqlalchemy.Float(),
        "chartist_forecast": sqlalchemy.Float(),
        "stock_account": sqlalchemy.Integer(),
        "cash_account": sqlalchemy.Float(),
    },
)
