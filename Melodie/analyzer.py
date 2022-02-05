from Melodie import create_db_conn


class Analyzer:
    def __init__(self, config):
        self.db_conn = create_db_conn(config)

    def all_scenarios(self):
        return self.db_conn.query_scenarios()

    def agent_result(self, agent_list_name: str, scenario_id: int = None,
                     agent_id: int = None, step: int = None):
        return self.db_conn.query_agent_results(agent_list_name, scenario_id, agent_id, step)

    def env_results(self, scenario_id: int = None, step: int = None):
        return self.db_conn.query_env_results()
