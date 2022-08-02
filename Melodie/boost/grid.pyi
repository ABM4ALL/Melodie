import random
from typing import ClassVar, Set, Dict, List, Tuple, TYPE_CHECKING, Optional, Type

import numpy as np

from .. import AgentList, Scenario

if TYPE_CHECKING:
    from .basics import Agent


class AgentIDManager:
    pass


class GridItem(Agent):
    x: int
    y: int
    grid: Grid

    def __init__(self, agent_id: int, x: int = 0, y: int = 0):
        pass


class GridAgent(GridItem):
    category: int

    def __init__(self, agent_id: int, x: int = 0, y: int = 0, grid: Grid = None):
        super().__init__(agent_id, x, y)

    def setup(self):
        pass

    def rand_move(self, x_range: int, y_range: int):
        pass

    def set_category(self):
        pass


class Spot(GridItem):
    role: int

    def __init__(self, spot_id: int, x: int = 0, y: int = 0):
        super(Spot, self).__init__(spot_id)

    def setup(self):
        pass

    def get_agent_ids(self) -> List[Tuple[int, int]]:
        pass


class Grid:
    scenario: "Scenario"
    wrap: bool

    def __init__(
        self, spot_cls: Type[Spot], scenario: Optional[Scenario] = None
    ): ...

    def setup_params(self, width: int, height: int,
                     wrap=True, caching=True, multi=True): ...

    def init_grid(self): ...

    def setup(self) -> None: ...

    def set_spot_attribute(self, attr_name: str, array_2d): ...

    def setup_agent_locations(
        self, agents: "AgentList", initial_placement: str = "none"
    ): ...

    def width(self) -> int: ...

    def height(self) -> int: ...

    def get_spot(self, x, y) -> "Spot": ...

    def get_agents(self, x: int, y: int) -> List[GridAgent]: ...

    def get_agent_ids(self, x: int, y: int) -> List[Tuple[int, int]]: ...

    def coords_wrap(self, x, y) -> Tuple[int, int]: ...

    def get_neighbors(
        self, x, y, radius: int = 1, moore=True, except_self=True
    ) -> List[Tuple[int, int]]: ...

    def get_neighbor_positions(
        self, x: int, y: int, radius=1, moore=True, except_self=True
    ) -> List[Tuple[int, int]]: ...

    def add_agent(self, agent: GridAgent) -> None: ...

    def remove_agent(self, agent: GridAgent) -> None: ...

    def move_agent(self, agent: GridAgent, target_x, target_y) -> None: ...

    def to_2d_array(self, attr_name: str) -> np.ndarray: ...

    def get_roles(self): ...

    def rand_move(
        self, agent: GridAgent, category: int, x_range: int, y_range: int
    ) -> Tuple[int, int]: ...

    def find_empty_spot(self) -> Tuple[int, int]: ...

    def choose_empty_place(self) -> Tuple[int, int]: ...

    def validate(self): ...

    def get_neighbors_info(
        self, x: int, y: int, radius: int = 1, moore=True, except_self=True
    ): ...

    def get_neighborhood(
        self, x: int, y: int, radius: int = 1, moore=True, except_self=True
    ) -> List[Spot]: ...

    def get_neighbors_info(self, x: int, y: int, radius: int = 1,
                         moore=True, except_self=True) -> List[Tuple[int, int]]: ...
