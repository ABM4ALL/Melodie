import sqlalchemy

from Melodie import DataFrameInfo
from Melodie import MatrixInfo
from tutorial.CovidContagion.source.data_info import id_age_group, id_health_state

simulator_scenarios = DataFrameInfo(
    df_name="simulator_scenarios",
    file_name="simulator_scenarios.xlsx",
    columns={
        "id": sqlalchemy.Integer(),
        "run_num": sqlalchemy.Integer(),
        "period_num": sqlalchemy.Integer(),
        "agent_num": sqlalchemy.Integer(),
        "grid_x_size": sqlalchemy.Integer(),
        "grid_y_size": sqlalchemy.Integer(),
        "initial_infected_percentage": sqlalchemy.Float(),
        "young_percentage": sqlalchemy.Float(),
        "infection_prob": sqlalchemy.Float(),
    },
)

id_age_group = id_age_group

id_health_state = id_health_state

agent_params = DataFrameInfo(
    df_name="agent_params",
    columns={
        "id_scenario": sqlalchemy.Integer(),
        "id": sqlalchemy.Integer(),
        "x": sqlalchemy.Integer(),
        "y": sqlalchemy.Integer(),
        "age_group": sqlalchemy.Integer(),
        "health_state": sqlalchemy.Integer(),
        "vaccination_trust_state": sqlalchemy.Integer(),
    },
)

grid_stay_prob = MatrixInfo(
    mat_name="grid_stay_prob",
    data_type=sqlalchemy.Float(),
    file_name="grid_stay_prob.xlsx",
)
