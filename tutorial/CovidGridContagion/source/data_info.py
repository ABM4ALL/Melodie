import sqlalchemy

from Melodie import DataFrameInfo
from Melodie import MatrixInfo

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

id_age_group = DataFrameInfo(
    df_name="id_age_group",
    file_name="id_age_group.xlsx",
    columns={
        "id": sqlalchemy.Integer(),
        "age_group": sqlalchemy.String(),
        "prob_s1_s1": sqlalchemy.Float(),
        "prob_s1_s2": sqlalchemy.Float(),
        "prob_s1_s3": sqlalchemy.Float(),
    },
)

id_health_state = DataFrameInfo(
    df_name="id_health_state",
    file_name="id_health_state.xlsx",
    columns={
        "id": sqlalchemy.Integer(),
        "health_state": sqlalchemy.String()
    },
)

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
