from Melodie import Visualizer
from .model import CovidModel
from MelodieInfra.lowcode.params import FloatParam


class CovidVisualizer(Visualizer):
    model: CovidModel

    def set_model(self, model: CovidModel):
        """
        Called when the visualizer is bound to a model instance.
        Set grid dimensions here (model is available now).
        """
        super().set_model(model)
        # Ensure grid dimensions are passed to frontend for correct scaling
        self.width = model.grid.width()
        self.height = model.grid.height()

    def setup(self):
        # Add interactive parameters to the left control panel
        self.params_manager.add_param(
            FloatParam(
                name="initial_infected_percentage",
                value_range=(0.0, 1.0),
                step=0.01,
                getter=lambda scenario: scenario.initial_infected_percentage,
                setter=lambda scenario, val: setattr(
                    scenario, "initial_infected_percentage", val
                ),
                label="Initial infected %",
                description="Share of agents initially infected (0-1).",
            )
        )
        self.params_manager.add_param(
            FloatParam(
                name="infection_prob",
                value_range=(0.0, 1.0),
                step=0.01,
                getter=lambda scenario: scenario.infection_prob,
                setter=lambda scenario, val: setattr(
                    scenario, "infection_prob", val
                ),
                label="Infection prob",
                description="Probability an infected agent infects a neighbor each step.",
            )
        )
        self.params_manager.add_param(
            FloatParam(
                name="recovery_prob",
                value_range=(0.0, 1.0),
                step=0.01,
                getter=lambda scenario: scenario.recovery_prob,
                setter=lambda scenario, val: setattr(
                    scenario, "recovery_prob", val
                ),
                label="Recovery prob",
                description="Probability an infected agent recovers each step.",
            )
        )

        # Configure the chart to show population health states over time
        self.plot_charts.add_line_chart("health_state_trend") \
            .set_data_source({
                "Susceptible": lambda: self.model.environment.num_susceptible,
                "Infected": lambda: self.model.environment.num_infected,
                "Recovered": lambda: self.model.environment.num_recovered
            })

        # Configure the grid visualization
        self.add_grid(
            name="covid_grid",
            grid_getter=lambda: self.model.grid,
            var_getter=lambda agent: agent.health_state,
            var_style={
                0: {"label": "Susceptible", "color": "#0000FF"},
                1: {"label": "Infected", "color": "#FF0000"},
                2: {"label": "Recovered", "color": "#808080"}
            },
            update_spots=False
        )
