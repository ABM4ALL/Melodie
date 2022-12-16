from typing import Set, List, Tuple, TYPE_CHECKING, Optional, Type

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

    def rand_move_agent(self, x_range: int, y_range: int):
        pass

    def set_category(self):
        pass


class Spot(GridItem):
    role: int

    def __init__(self, spot_id: int, x: int = 0, y: int = 0):
        super(Spot, self).__init__(spot_id)

    def setup(self):
        pass

    def get_spot_agents(self) -> List[Tuple[int, int]]:
        pass


SpotGeneric = TypeVar("SpotGeneric")


class Grid(typing.Sequence[AgentGeneric]):
    scenario: "Scenario"
    wrap: bool

    def __init__(self, spot_cls: Type[Spot], scenario: Optional[Scenario] = None): ...

    def setup_params(
            self, width: int, height: int, wrap=True, caching=True, multi=True
    ): ...

    def init_grid(self): ...

    def setup(self) -> None: ...

    def set_spot_property(self, attr_name: str, array_2d): ...

    def setup_agent_locations(
            self, agents: "AgentList", initial_placement: str = "none"
    ): ...

    def width(self) -> int: ...

    def height(self) -> int: ...

    def get_spot(self, x, y) -> "SpotGeneric": ...

    def get_spot_agents(self, spot: Spot) -> List[Tuple[int, int]]: ...

    def coords_wrap(self, x, y) -> Tuple[int, int]: ...

    def get_neighbors(
            self, agent: GridAgent, radius: int = 1, moore=True, except_self=True
    ) -> List[Tuple[int, int]]: ...

    def _get_neighbor_positions(
            self, x: int, y: int, radius=1, moore=True, except_self=True
    ) -> List[Tuple[int, int]]: ...

    def add_agent(self, agent: GridAgent) -> None: ...

    def remove_agent(self, agent: GridAgent) -> None: ...

    def move_agent(self, agent: GridAgent, target_x, target_y) -> None: ...

    def to_2d_array(self, attr_name: str) -> np.ndarray: ...

    def get_colormap(self): ...

    def rand_move_agent(
            self, agent: GridAgent, category: int, x_range: int, y_range: int
    ) -> Tuple[int, int]: ...

    def find_empty_spot(self) -> Tuple[int, int]: ...

    def _get_neighborhood(
            self, x: int, y: int, radius: int = 1, moore=True, except_self=True
    ) -> List[Spot]: ...

    def get_empty_spots(self) -> Set[Tuple[int, int]]: ...

    def get_agent_neighborhood(
            self, agent: GridAgent, radius=1, moore=True, except_self=True
    ): ...

    def get_spot_neighborhood(
            self, spot: SpotGeneric, radius=1, moore=True, except_self=True
    ): ...

    @property
    def get_agent_categories(self) -> Set[int]:
        ...

    def get_agent_container(self, category_id) -> AgentList:
        ...
