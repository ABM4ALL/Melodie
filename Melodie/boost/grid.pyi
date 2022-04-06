import functools
import random
from turtle import st
from typing import ClassVar, Set, Dict, List, Tuple, TYPE_CHECKING

import numpy as np

from .. import AgentList

if TYPE_CHECKING:
    from .basics import Agent
    from ..boost.vectorize import vectorize_2d


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


class Spot(Agent):
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
        self._spots = [[spot_cls(self._convert_to_1d(x, y), x, y)
                        for x in range(width)] for y in range(height)]
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
        Add agent category
        :param category_name:
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
        x, y = self._bound_check(x, y)
        neighbors = []
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if not moore and abs(dx) + abs(dy) > radius:
                    continue
                if not self.wrap and not self._in_bounds(x + dx, y + dy):
                    continue
                if dx == 0 and dy == 0 and except_self:
                    continue
                neighbors.append(self._bound_check(x + dx, y + dy))
        return neighbors

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
        grid_roles = np.zeros((self.height * self.width, 4))
        for x in range(self.width):
            for y in range(self.height):
                spot = self.get_spot(x, y)
                # role = spot.role
                pos_1d = self._convert_to_1d(x, y)
                grid_roles[pos_1d, 0] = x
                grid_roles[pos_1d, 1] = y
                grid_roles[pos_1d, 2] = 0
                grid_roles[pos_1d, 3] = spot.role
        return grid_roles

    def rand_move(self, agent_id: GridAgent, category: int, x_range: int, y_range: int):

        source_x, source_y = self.get_agent_pos(agent_id, category)
        self._remove_agent(agent_id, category, source_x, source_y)
        dx = random.randint(-x_range, x_range)
        dy = random.randint(-y_range, y_range)
        target_x = source_x + dx
        target_y = source_y + dy
        self.add_agent(agent_id, category, target_x, target_y)
        return target_x, target_y

    def find_empty_spot(self) -> Tuple[int, int]:
        ...

    def choose_empty_place(self) -> Tuple[int, int]:
        ...
