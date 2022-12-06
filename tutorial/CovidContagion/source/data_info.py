import sqlalchemy

from Melodie import DataFrameInfo

simulator_scenarios = DataFrameInfo(
    df_name="simulator_scenarios",
    file_name="SimulatorScenarios.xlsx",
    columns={
        "id": sqlalchemy.Integer(),
        "run_num": sqlalchemy.Integer(),
        "period_num": sqlalchemy.Integer(),
        "agent_num": sqlalchemy.Integer(),
        "initial_infected_percentage": sqlalchemy.Float(),
        "young_percentage": sqlalchemy.Float(),
        "infection_prob": sqlalchemy.Float(),
    },
)

id_health_state = DataFrameInfo(
    df_name="ID_HealthState",
    file_name="ID_HealthState.xlsx",
    columns={
        "id": sqlalchemy.Integer(),
        "health_state": sqlalchemy.String()
    },
)

id_age_group = DataFrameInfo(
    df_name="ID_AgeGroup",
    file_name="ID_AgeGroup.xlsx",
    columns={
        "id": sqlalchemy.Integer(),
        "name": sqlalchemy.String(),
    },
)

transition_prob = DataFrameInfo(
    df_name="Parameter_AgeGroup_TransitionProb",
    file_name="Parameter_AgeGroup_TransitionProb.xlsx",
    columns={
        "id_age_group": sqlalchemy.Integer(),
        "prob_s1_s1": sqlalchemy.Float(),
        "prob_s1_s2": sqlalchemy.Float(),
        "prob_s1_s3": sqlalchemy.Float(),
    },
)

agent_params = DataFrameInfo(
    df_name="agent_params",
    columns={
        "id_scenario": sqlalchemy.Integer(),
        "id": sqlalchemy.Integer(),
        "age_group": sqlalchemy.Integer(),
        "health_state": sqlalchemy.Integer(),
    },
)
