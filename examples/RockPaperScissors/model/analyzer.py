from Melodie import Analyzer


class RPSAnalyzer(Analyzer):
    def setup(self):
        self.trainer_scenarios = "trainer_scenarios"
        self.agent_trainer_result = "agent_trainer_result"
        self.agent_trainer_result_cov = "agent_trainer_result_cov"
        self.env_trainer_result = "env_trainer_result"
        self.env_trainer_result_cov = "env_trainer_result_cov"

    def plot_agent_strategy_convergence(self, trainer_scenario_id, generation_num):
        agent_trainer_result_cov = self.read_dataframe(self.agent_trainer_result_cov)
        strategy_params = ["strategy_param_1", "strategy_param_2", "strategy_param_3"]
        strategy_params_labels = [
            r"$\alpha_{i, 1}$",
            r"$\alpha_{i, 2}$",
            r"$\alpha_{i, 3}$",
        ]

        ylim_heatmap = (0, 1)
        fig_suffix_heatmap = "_TS" + str(trainer_scenario_id) + "G" + str(0)
        self.plot_trainer_agent_strategy_params_convergence_heatmap(
            agent_trainer_result_cov,
            strategy_params,
            trainer_scenario_id,
            generation_id=0,
            ylim=ylim_heatmap,
            strategy_params_labels=strategy_params_labels,
            fig_suffix=fig_suffix_heatmap,
        )

        last_generation_id = generation_num - 1
        fig_suffix_heatmap = (
            "_TS" + str(trainer_scenario_id) + "G" + str(last_generation_id)
        )
        self.plot_trainer_agent_strategy_params_convergence_heatmap(
            agent_trainer_result_cov,
            strategy_params,
            trainer_scenario_id,
            generation_id=last_generation_id,
            ylim=ylim_heatmap,
            strategy_params_labels=strategy_params_labels,
            fig_suffix=fig_suffix_heatmap,
        )

        ylim_lines = (-1, 2)
        fig_suffix_lines = "_TS" + str(trainer_scenario_id)
        self.plot_trainer_agent_strategy_params_convergence_lines(
            agent_trainer_result_cov,
            strategy_params,
            trainer_scenario_id,
            ylim=ylim_lines,
            strategy_params_labels=strategy_params_labels,
            fig_suffix=fig_suffix_lines,
        )

    def plot_env_var_evolution(self, trainer_scenario_id: int):
        var_name = "agents_total_payoff"
        env_trainer_result_cov = self.read_dataframe(self.env_trainer_result_cov)
        fig_suffix = "_" + var_name + "_" + "TS" + str(trainer_scenario_id)
        self.plot_trainer_env_var_evolution_lines(
            var_name,
            env_trainer_result_cov,
            trainer_scenario_id=trainer_scenario_id,
            y_label="Agents Total Payoff",
            y_lim=(0, 10000),
            legend_ncol=5,
            fig_suffix=fig_suffix,
        )

    def run(self):

        self.plot_agent_strategy_convergence(0, 100)
        self.plot_env_var_evolution(0)
