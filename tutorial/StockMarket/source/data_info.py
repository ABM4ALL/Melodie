import sqlalchemy

from Melodie import DataFrameInfo

simulator_scenarios = DataFrameInfo(
    df_name="simulator_scenarios",
    file_name="simulator_scenarios.xlsx",
    columns={
        "id": sqlalchemy.Integer(),
        "run_num": sqlalchemy.Integer(),
        "period_num": sqlalchemy.Integer(),
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

trainer_scenarios = DataFrameInfo(
    df_name="trainer_scenarios",
    file_name="trainer_scenarios.xlsx",
    columns={
        "id": sqlalchemy.Integer(),
        "period_num": sqlalchemy.Integer(),
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

calibrator_scenarios = DataFrameInfo(
    df_name="calibrator_scenarios",
    file_name="calibrator_scenarios.xlsx",
    columns={
        "id": sqlalchemy.Integer(),
        "period_num": sqlalchemy.Integer(),
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

trainer_params_scenarios = DataFrameInfo(
    df_name="trainer_params_scenarios",
    file_name="trainer_params_scenarios.xlsx",
    columns={
        "id": sqlalchemy.Integer(),
        # "period_num": sqlalchemy.Integer(),
        # "period_ticks": sqlalchemy.Integer(),
        # "agent_num": sqlalchemy.Integer(),
        "strategy_population": sqlalchemy.Integer(),
        "mutation_prob": sqlalchemy.Float(),
        "strategy_param_code_length": sqlalchemy.Integer(),
        "path_num": sqlalchemy.Integer(),
        "generation_num": sqlalchemy.Integer(),
        "fundamentalist_weight_min": sqlalchemy.Float(),
        "fundamentalist_weight_max": sqlalchemy.Float(),
    },
)

calibrator_params_scenarios = DataFrameInfo(
    df_name="calibrator_params_scenarios",
    file_name="calibrator_params_scenarios.xlsx",
    columns={
        "id": sqlalchemy.Integer(),
        "strategy_population": sqlalchemy.Integer(),
        "mutation_prob": sqlalchemy.Float(),
        "strategy_param_code_length": sqlalchemy.Integer(),
        "path_num": sqlalchemy.Integer(),
        "generation_num": sqlalchemy.Integer(),
        "fundamentalist_weight_max_min": sqlalchemy.Float(),
        "fundamentalist_weight_max_max": sqlalchemy.Float(),
    },
)

calibrator_target = DataFrameInfo(
    df_name="calibrator_target",
    file_name="calibrator_target.xlsx",
    columns={
        "period": sqlalchemy.Integer(),
        "open": sqlalchemy.Float(),
        "high": sqlalchemy.Float(),
        "low": sqlalchemy.Float(),
        "mean": sqlalchemy.Float(),
        "close": sqlalchemy.Float(),
        "volume": sqlalchemy.Float(),
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
