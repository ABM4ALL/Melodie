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
    },
)
