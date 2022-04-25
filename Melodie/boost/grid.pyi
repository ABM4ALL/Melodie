import random
from typing import ClassVar, Set, Dict, List, Tuple, TYPE_CHECKING

import numpy as np

from .. import AgentList

if TYPE_CHECKING:
    from .basics import Agent
    from ..boost.vectorize import vectorize_2d


class AgentIDManager:
    pass


class GridItem(Agent):
    x: int
    y: int

    def __init__(self, agent_id: int, x: int = 0, y: int = 0):
        pass


class GridAgent(GridItem):
    category: int

    def __init__(self, agent_id: int, x: int = 0, y: int = 0, category: int = 0):
        super().__init__(agent_id, x, y)

    def setup(self):
        pass


class Spot(GridItem):
    role: int

    def __init__(self, spot_id: int, x: int = 0, y: int = 0):
        super(Spot, self).__init__(spot_id)

    def setup(self):
        pass


class Grid:
    """
    Grid is a widely-used discrete space for ABM.
    Grid contains many `Spot`s, each `Spot` could contain several agents.
    """

    def __init__(self, spot_cls: ClassVar[Spot], width: int, height: int, wrap=True, caching=True,
                 multi=True):
        """

        :param spot_cls: The class of Spot
        :param width: The width of Grid
        :param height: The height of Grid
        :param wrap: If true, the coordinate overflow will be mapped to another end.
        :param caching: If true, the neighbors and bound check results will be cached to avoid re-computing.

        """
        self.wrap = wrap
        self._spots: List[List[Spot]] = []
        for x in range(self.width):
            for y in range(self.height):
                self._spots[y][x].setup()
        self._agent_ids: Dict[str, List[Set[int]]] = {}

    def width(self) -> int:
        ...

    def height(self) -> int:
        ...

    def add_agent_container(self, category_id: int, container: AgentList, initial_placement: str = "none") -> None:
        """
        Add agent container

        :param category_id: A integer stand for category. It's better to define it as a global variable.
        :param container: The Agent container object
        :param initial_placement: Whether/How the agents in the agent container will be placed on the grid initially.
        :return:
        """

    def get_spot(self, x, y) -> "Spot":
        """
        Get a spot at position (x, y)
        :param x:
        :param y:
        :return:
        """

    def get_agents(self, x: int, y: int) -> List[GridAgent]:
        ...

    def get_agent_ids(self, x: int, y: int) -> List[Tuple[int, int]]:
        """
        Get all agent of a specific category from the spot at (x, y)
        :param x:
        :param y:
        :return: A set of (int, int) standing for (agent_id, category), the agent ids.
        """

    def coords_wrap(self, x, y):
        """
        Wrap the coordination
        :param x:
        :param y:
        :return:
        """
        return x % self.width, y % self.height

    def get_neighbors(self, x, y, radius: int = 1, moore=True, except_self=True) -> List[Tuple[int, int]]:
        """
        Get the neighbors of some spot.
        :param x:
        :param y:
        :param radius:
        :param moore:
        :param except_self:
        :return:
        """
        ...

    def add_agent(self, agent: GridAgent, category: int) -> None:
        """
        Add agent onto the grid
        :param agent:
        :param category:
        :return:
        """
        ...

    def remove_agent(self, agent: GridAgent, category: int) -> None:
        """
        Remove agent from the grid
        :param agent:
        :param category:
        :return:
        """
        ...

    def move_agent(self, agent: GridAgent, category: int, target_x, target_y) -> None:
        """
        Move agent to target position.
        :param agent:
        :param category:
        :param target_x:
        :param target_y:
        :return:
        """
        ...

    def to_2d_array(self, attr_name: str) -> np.ndarray:
        """
        Collect attribute of each spot and write the attribute value into an 2d np.array.
        Notice:
        - The attribute to collect should be float/int/bool, not other types such as str.
        - If you would like to get an element from the returned array, please write like this:
         ```python
         arr = self.to_2d_array('some_attr')
         y = 10
         x = 5
         spot_at_x_5_y_10 = arr[y][x] # CORRECT. Get the some_attr value of spot at `x = 5, y = 10`
         spot_at_x_5_y_10 = arr[x][y] # INCORRECT. You will get the value of spot at `x = 10, y = 5`
         ```

        :param attr_name: the attribute name to collect for this model.
        :return:
        """
        return vectorize_2d(self._spots, attr_name)

    def get_roles(self):
        ...

    def rand_move(self, agent_id: GridAgent, category: int, x_range: int, y_range: int) -> Tuple[int, int]:
        ...

    def find_empty_spot(self) -> Tuple[int, int]:
        ...

    def choose_empty_place(self) -> Tuple[int, int]:
        ...

    def validate(self):
        pass
