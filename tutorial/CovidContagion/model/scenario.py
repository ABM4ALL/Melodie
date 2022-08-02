from Melodie import Scenario
from tutorial.CovidContagion.model import data_info as df_info


class CovidScenario(Scenario):
    def setup(self):
        self.periods = 0
        self.period_hours = 0
        self.agent_num = 0
        self.grid_x_size = 0
        self.grid_y_size = 0
        self.initial_infected_percentage = 0.0
        self.young_percentage = 0.0
        self.network_type = 0
        self.network_param_k = 0
        self.network_param_p = 0.0
        self.network_param_m = 0
        self.network_param_threshold = 0.0
        self.vaccination_trust_percentage = 0.0
        self.vaccination_ad_percentage = 0.0
        self.vaccination_ad_success_prob = 0.0
        self.vaccination_action_prob = 0.0
        self.infection_prob = 0.0
        self.reinfection_prob = 0.0
        self.vaccinated_infection_prob = 0.0
        self.setup_age_group_params()

    def setup_age_group_params(self):
        df = self.get_dataframe(df_info.id_age_group)
        self.ag0_prob_s1_s1 = df.at[0, "prob_s1_s1"]
        self.ag0_prob_s1_s2 = df.at[0, "prob_s1_s2"]
        self.ag0_prob_s1_s3 = df.at[0, "prob_s1_s3"]
        self.ag0_move_radius = df.at[0, "move_radius"]
        self.ag1_prob_s1_s1 = df.at[1, "prob_s1_s1"]
        self.ag1_prob_s1_s2 = df.at[1, "prob_s1_s2"]
        self.ag1_prob_s1_s3 = df.at[1, "prob_s1_s3"]
        self.ag1_move_radius = df.at[1, "move_radius"]

    def get_infection_prob(self, health_state: int) -> float:
        if health_state == 0:
            return self.infection_prob
        elif health_state == 2:
            return self.reinfection_prob
        elif health_state == 4:
            return self.vaccinated_infection_prob
        else:
            # This person won't be infected again, now.
            pass

    def get_state_transition_prob(self, id_age_group: int) -> tuple:
        if id_age_group == 0:
            return self.ag0_prob_s1_s1, self.ag0_prob_s1_s2, self.ag0_prob_s1_s3
        elif id_age_group == 1:
            return self.ag1_prob_s1_s1, self.ag1_prob_s1_s2, self.ag1_prob_s1_s3
        else:
            # This person has wierd age group.
            pass

    def get_move_radius(self, id_age_group: int) -> int:
        if id_age_group == 0:
            return self.ag0_move_radius
        elif id_age_group == 1:
            return self.ag1_move_radius
        else:
            # This person has wierd age group.
            pass
