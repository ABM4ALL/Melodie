import sqlalchemy

from Melodie import DataFrameInfo
from tutorial.CovidContagion.source.data_info import id_age_group
from tutorial.CovidContagion.source.data_info import id_health_state
from tutorial.CovidContagion.source.data_info import agent_params


simulator_scenarios = DataFrameInfo(
    df_name="simulator_scenarios",
    file_name="simulator_scenarios.xlsx",
    columns={
        "id": sqlalchemy.Integer(),
        "run_num": sqlalchemy.Integer(),
        "period_num": sqlalchemy.Integer(),
        "agent_num": sqlalchemy.Integer(),
        "initial_infected_percentage": sqlalchemy.Float(),
        "young_percentage": sqlalchemy.Float(),
        "network_type": sqlalchemy.String(),
        "network_param_k": sqlalchemy.Integer(),
        "network_param_p": sqlalchemy.Float(),
        "network_param_m": sqlalchemy.Integer(),
        "infection_prob": sqlalchemy.Float(),
    },
)

id_age_group = id_age_group

id_health_state = id_health_state

agent_params = agent_params
