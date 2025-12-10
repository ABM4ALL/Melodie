from Melodie import Visualizer
from .model import CovidModel


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
        # Configure the chart to show population health states over time
        def get_susceptible():
            val = self.model.environment.num_susceptible
            print(f"[DEBUG] Susceptible: {val}")
            return val
        
        def get_infected():
            val = self.model.environment.num_infected
            print(f"[DEBUG] Infected: {val}")
            return val
        
        def get_recovered():
            val = self.model.environment.num_recovered
            print(f"[DEBUG] Recovered: {val}")
            return val
        
        self.plot_charts.add_line_chart("health_state_trend") \
            .set_data_source({
                "Susceptible": get_susceptible,
                "Infected": get_infected,
                "Recovered": get_recovered
            })

        # Configure the grid visualization
        self.add_grid(
            name="covid_grid",
            grid_getter=lambda: self.model.grid,
            var_getter=lambda agent: agent.health_state,
            var_style={
                0: {"label": "Susceptible", "color": "#00FF00"},
                1: {"label": "Infected", "color": "#FF0000"},
                2: {"label": "Recovered", "color": "#808080"}
            },
            update_spots=False
        )
