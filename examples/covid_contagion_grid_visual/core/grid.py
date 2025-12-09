from Melodie import Grid, Spot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .scenario import CovidScenario


class CovidSpot(Spot):
    """
    Represents a single cell on the grid.
    Can hold properties that affect agent behavior, like 'stay_prob'.
    """

    def setup(self) -> None:
        self.stay_prob: float = 0.0


class CovidGrid(Grid):
    """
    Manages the 2D space, spots, and agent positions.
    """
    
    scenario: "CovidScenario"

    def setup(self) -> None:
        """
        Configure the grid.
        Here we apply the 'stay_prob' matrix loaded in the scenario to the spots.
        """
        # set_spot_property loads a 2D numpy array or list of lists into the grid spots
        self.set_spot_property("stay_prob", self.scenario.stay_prob_matrix)
