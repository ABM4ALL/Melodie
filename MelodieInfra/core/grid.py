from typing import ClassVar, Dict, List, Tuple

from MelodieInfra.core.agent_list import AgentList

from .agent import Agent
from .api import _random as random
from .api import floor, iterable, lru_cache, randint


class GridItem(Agent):
    _unserializable_props_ = ("model", "scenario", "grid")

    def __init__(self, agent_id: int, grid, x: int = 0, y: int = 0):
        super().__init__(agent_id)
        self.grid = grid
        self.x = x
        self.y = y


class GridAgent(GridItem):
    def __init__(self, agent_id: int, x: int = 0, y: int = 0, grid=None):
        super().__init__(agent_id, grid, x, y)
        self.category = -1
        self.set_category()
        assert self.category >= 0, "Category should be larger or "

    def set_category(self) -> int:
        """
        Set the category of GridAgent.

        As there may be more than one types of agent wandering around the grid, `category` is used to tell the type of
        `GridAgent`. So be sure to inherit this method in custom GridAgent implementation.

        :return: int
        """
        raise NotImplementedError("Category should be set for GridAgent")

    def rand_move_agent(self, x_range, y_range):
        """
        Randomly move to a new position within x and y range.

        :return: None
        """
        if self.grid is None:
            raise ValueError("Grid Agent has not been registered onto the grid!")
        self.x, self.y = self.grid.rand_move_agent(
            self, self.category, x_range, y_range
        )


class Spot(GridItem):
    def __init__(self, spot_id: int, grid: "Grid", x: int = 0, y: int = 0):
        super().__init__(spot_id, grid, x, y)
        self.grid = grid
        self.colormap = 0

    def get_spot_agents(self):
        """
        Get all agents on the spot.

        :return: a list of grid agent.
        """
        return self.grid.get_spot_agents(self)

    def get_style(self):
        return {"backgroundColor": "#ffffff"}


class Grid:
    """
    Grid is a widely-used discrete space for ABM.
    Grid contains many `Spot`s, each `Spot` could contain several agents.
    """

    def __init__(self, spot_cls: ClassVar[Spot], scenario=None):
        """
        :param spot_cls: The class of Spot
        :param width: The width of Grid
        :param height: The height of Grid
        :param wrap: If true, the coordinate overflow will be mapped to another end.
        :param caching: If true, the neighbors and bound check results will be cached to avoid re-computing.
        """
        self._width = -1
        self._height = -1
        self._wrap = False
        self._caching = True
        self._multi = False

        self._spot_cls = spot_cls
        self._existed_agents: Dict[str, Dict[int, Tuple[int, int]]] = {}
        self._agent_ids: "Dict[str, List[Set[int]]]" = {}
        self._spots = []
        self.scenario = scenario
        self._empty_spots = set()
        self._agent_containers = {}
        self._cache = {}

    def init_grid(self):
        SpotCls = self._spot_cls
        self._spots = [
            [SpotCls(self._convert_to_1d(x, y), self, x, y) for x in range(self._width)]
            for y in range(self._height)
        ]
        for x in range(self._width):
            for y in range(self._height):
                self._spots[y][x].setup()
                self._empty_spots.add(self._convert_to_1d(x, y))
        self._roles_list = [
            [0 for j in range(4)] for i in range(self._width * self._height)
        ]
        # if self._caching:
        #     self.enable_caching()

    # def enable_caching(self):
    #     self.get_neighbors = lru_cache(
    #         self._width * self._height)(self.get_neighbors)
    # self._bound_check = lru_cache(
    #     self._width * self._height)(self._bound_check)

    def setup_params(
        self, width: int, height: int, wrap=True, caching=True, multi=True
    ):
        """
        Setup the parameters of the grid.

        :param width: An integer for the grid width.
        :param height: An integer for the grid height.
        :param wrap: A boolean (default True). If True, an agent moving out of
            the grid on one side will re-enter from the opposite side.
        :param caching: A boolean (default True). If True, the grid caches the
            neighbors of each spot to improve performance.
        :param multi: A boolean (default True). If True, more than one agent can
            stand on the same spot. If False, an error will be raised when
            attempting to place multiple agents on one spot.
        :return: None
        """
        self._width = width
        self._height = height
        self._wrap = wrap
        self._caching = caching
        self._multi = multi
        self.init_grid()

    def setup(self):
        """
        Be sure to inherit this function.

        :return: None
        """
        pass

    def _setup(self):
        self.setup()

    def add_category(self, category_name: str):
        """
        Add agent category
        :param category_name:
        :return:
        """
        self._agent_ids[category_name] = [
            set() for i in range(self._width * self._height)
        ]
        self._existed_agents[category_name] = {}

    def get_spot(self, x, y) -> "Spot":
        """
        Get a ``Spot`` at position ``(x, y)``

        :param x:
        :param y:
        :return: The ``Spot`` at position (x, y)
        """
        x, y = self._bound_check(x, y)
        return self._spots[y][x]

    def get_agent_ids(self, category: str, x: int, y: int) -> "Set[int]":
        """
        Get all agent of a specific category from the spot at (x, y)
        :param category:
        :param x:
        :param y:
        :return: A set of int, the agent ids.
        """
        agent_ids = self._agent_ids[category][self._convert_to_1d(x, y)]
        if agent_ids is None:
            raise KeyError(f"Category {category} not registered!")
        return agent_ids

    def _convert_to_1d(self, x, y):
        return x * self._height + y

    def _num_to_2d_coor(self, num: int):
        return floor(num / self._height), num % self._width

    def _in_bounds(self, x, y):
        return (0 <= x < self.width) and (0 <= y <= self._height)

    def _get_category_of_agents(self, category_name: str):
        # category = self._existed_agents.get(category_name)

        # raise ValueError(f"Category {category_name} is not registered!")
        return self._existed_agents[category_name]

    def _bound_check(self, x, y):
        if self._wrap:
            return self.coords_wrap(x, y)
        if not (0 <= x < self._width):
            raise IndexError("grid index x was out of range")
        elif not (0 <= y <= self._height):
            raise IndexError("grid index y was out of range")
        else:
            return x, y

    def coords_wrap(self, x, y):
        """
        Wrap the coordination
        :param x:
        :param y:
        :return:
        """
        x_wrapped, y_wrapped = x % self._width, y % self._height
        x_wrapped = x_wrapped if x_wrapped >= 0 else self._width + x_wrapped
        y_wrapped = y_wrapped if y_wrapped >= 0 else self._height + y_wrapped
        return x_wrapped, y_wrapped

    def _get_neighbor_positions(
        self, x, y, radius: int = 1, moore=True, except_self=True
    ) -> List[Tuple[int, int]]:
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
        # s = except_self+moore*2**1+radius*2**10+x*2**20+y*2**30
        s = f"{except_self}+{moore}+{radius}+{x}+{y}"
        if s not in self._cache:
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if not moore and abs(dx) + abs(dy) > radius:
                        continue
                    if not self._wrap and not self._in_bounds(x + dx, y + dy):
                        continue
                    if dx == 0 and dy == 0 and except_self:
                        continue
                    neighbors.append(self._bound_check(x + dx, y + dy))
            self._cache[s] = neighbors
            return neighbors
        else:
            return self._cache[s]
        # s = except_self+moore*2**1+radius*2**10+x*2**20+y*2**30
        # if s not in self._cache:
        #     neighbors = []
        #     for dx in range(-radius, radius + 1):
        #         for dy in range(-radius, radius + 1):
        #             if not moore and abs(dx) + abs(dy) > radius:
        #                 continue
        #             if not self._wrap and not self._in_bounds(x + dx, y + dy):
        #                 continue
        #             if dx == 0 and dy == 0 and except_self:
        #                 continue
        #             neighbors.append(self._bound_check(x + dx, y + dy))
        #     self._cache[s] = neighbors
        #     return neighbors
        # else:
        #     return self._cache[s]

    def _get_neighborhood(self, x, y, radius=1, moore=True, except_self=True):
        """
        Get all spots around (x, y)

        """
        neighbor_positions = self._get_neighbor_positions(
            x, y, radius, moore, except_self
        )
        spots = []
        for pos in neighbor_positions:
            x, y = pos
            spots.append(self.get_spot(x, y))
        return spots

    def get_agent_neighborhood(self, agent, radius=1, moore=True, except_self=True):
        return self._get_neighborhood(agent.x, agent.y, radius, moore, except_self)

    def get_spot_neighborhood(self, spot, radius=1, moore=True, except_self=True):
        return self._get_neighborhood(spot.x, spot.y, radius, moore, except_self)

    def add_agent(self, agent: GridAgent):
        """
        Add an agent to the grid

        :param agent: An GridAgent object.
        :param category: A string, the name of category. The category should be registered.
        :return:
        """
        if not isinstance(agent, GridAgent):
            raise TypeError(
                f"Parameter `agent` should be of type {GridAgent.__name__} "
            )
        agent.grid = self
        self._add_agent(agent.id, agent.category, agent.x, agent.y)

    def _add_agent(self, agent_id: int, category: str, x: int, y: int):
        """
        Add agent onto the grid
        :param agent_id:
        :param category:
        :param x:
        :param y:
        :return:
        """
        x, y = self._bound_check(x, y)
        if category not in self._existed_agents:
            self._existed_agents[category] = {}
        if category not in self._agent_ids:
            l = []
            for _ in range(self._width * self._height):
                l.append(set())
            self._agent_ids[category] = l  # = [set()
            #  for _ in range(self._width * self._height)]

        category_of_agents = self._get_category_of_agents(category)

        if agent_id in category_of_agents:
            raise ValueError(f"Agent with id: {agent_id} already exists on grid!")
        pos_1d = self._convert_to_1d(x, y)
        if agent_id in self._agent_ids[category][pos_1d]:
            raise ValueError(
                f"Agent with id: {agent_id} already exists at position {(x, y)}!"
            )
        else:
            self._agent_ids[category][pos_1d].add(agent_id)
            self._existed_agents[category][agent_id] = (x, y)
        if pos_1d in self._empty_spots:
            self._empty_spots.remove(pos_1d)

    def _remove_agent(self, agent_id: int, category: str, x: int, y: int):
        x, y = self._bound_check(x, y)

        category_of_agents = self._get_category_of_agents(category)

        if agent_id not in category_of_agents.keys():
            raise ValueError(f"Agent with id: {agent_id} does not exist on grid!")
        pos_1d = self._convert_to_1d(x, y)
        if agent_id not in self._existed_agents[category]:
            raise ValueError("Agent does not exist on the grid!")
        if agent_id not in self._agent_ids[category][pos_1d]:
            print("Melodie-boost error occured. agent_id:", agent_id, "x:", x, "y:", y)
            raise IndexError("agent_id does not exist on such coordinate.")
        else:
            self._agent_ids[category][pos_1d].remove(agent_id)
            self._existed_agents[category].pop(agent_id)

        agents = self._get_spot_agents(pos_1d)
        if len(agents) == 0:
            self._empty_spots.add(pos_1d)

    def remove_agent(self, agent: GridAgent):
        """
        Remove agent from the grid

        :param agent:
        :return:
        """
        source_x, source_y = self.get_agent_pos(agent.id, agent.category)
        self._remove_agent(agent.id, agent.category, source_x, source_y)

    def move_agent(self, agent: GridAgent, target_x, target_y):
        """
        Move agent to target position.
        :param agent_id:
        :param category:
        :param target_x:
        :param target_y:
        :return:
        """
        source_x, source_y = self.get_agent_pos(agent.id, agent.category)
        self._remove_agent(agent.id, agent.category, source_x, source_y)
        self._add_agent(agent.id, agent.category, target_x, target_y)
        agent.x, agent.y = target_x, target_y

    def get_agent_pos(self, agent_id: int, category: str) -> Tuple[int, int]:
        """
        Get the agent position at the grid.
        :param agent_id:
        :param category:
        :return:
        """
        return self._existed_agents[category][agent_id]

    def height(self):
        """
        Get the height of grid

        :return: height, an ``int``
        """
        return self._height

    def width(self):
        """
        Get the width of grid

        :return: width, an ``int``
        """
        return self._width

    def get_neighbors(self, agent: GridAgent, radius=1, moore=True, except_self=True):
        """
        Get the neighbors of one spot at (x, y).

        :param x:
        :param y:
        :param radius:
        :param moore:
        :param except_self:
        :return:  A list of the tuple: (`Agent category`, `Agent id`).
        """
        neighbor_ids = []
        neighbor_positions = self._get_neighbor_positions(
            agent.x, agent.y, radius, moore, except_self
        )
        for neighbor_pos in neighbor_positions:
            x, y = neighbor_pos
            agent_ids = self.get_spot_agents(self.get_spot(x, y))
            neighbor_ids.extend(agent_ids)
        return neighbor_ids

    def get_spot_agents(self, spot: Spot):
        """
        Get agents on the spot.

        """
        return self._get_spot_agents(spot.id)

    def _get_spot_agents(self, spot_id: int):
        l = []
        for item in iterable(self._agent_ids.items()):
            category, spot_set_list = item
            for agent_id in spot_set_list[spot_id]:
                l.append((category, agent_id))
        return l

    def get_colormap(self):
        """
        Get the role of each spot.

        :return: A tuple. The first item is a nested list for spot roles, and the second item is a dict for agent roles.
        """

        agents_series_data = {}
        for category in self._agent_ids.keys():
            agents_series_data[category] = []
        for x in range(self._width):
            for y in range(self._height):
                spot = self.get_spot(x, y)
                pos_1d = self._convert_to_1d(x, y)
                role_pos_list = self._roles_list[pos_1d]
                role_pos_list[0] = x
                role_pos_list[1] = y
                role_pos_list[2] = 0
                role_pos_list[3] = spot.colormap
                for agent_desc in self.get_spot_agents(spot):
                    agent_category, agent_id = agent_desc
                    series_data_one_category = agents_series_data[agent_category]
                    series_data_one_category.append(
                        {
                            "value": [x, y],
                            "id": agent_id,
                            "category": agent_category,
                        }
                    )

        return self._roles_list, agents_series_data

    def spots_to_json(self):
        """
        Convert spots in this grid into a list of json-serializable dict

        :return: JSON serializable list
        """
        spots_serialized = []
        for x in range(self.width()):
            for y in range(self.height()):
                spot: Spot = self._spots[y][x]
                spots_serialized.append(spot.to_json())
        return spots_serialized

    def get_empty_spots(self):
        """
        Get all empty spots from grid.

        :return: a list of empty spot coordinates.
        """
        positions = []
        for spot_pos_1d in self._empty_spots:
            positions.append(self._num_to_2d_coor(spot_pos_1d))
        return positions

    def find_empty_spot(self):
        rand_value = randint(0, len(self._empty_spots) - 1)
        i = 0
        for item in self._empty_spots:
            if i == rand_value:
                return self._num_to_2d_coor(item)
            i += 1

    def setup_agent_locations(self, category, initial_placement="direct") -> None:
        """
        Add an agent category.

        For example, if there are two classes of agents: `Wolf(GridAgent)` and `Sheep(GridAgent)`,
        and there are 100 agents with id 0~99 for each class. It is obvious in such a circumstance that
        we cannot identify an agent only with agent *id*.So it is essential to use *category_name* to distinguish two types of agents.

        :param category_id: The id of new category.
        :param category: An AgentList object
        :param initial_placement: A str object stand for initial placement.
        :return: None
        """
        initial_placement = initial_placement.lower()
        self._add_agent_container(category, initial_placement)

    def _add_agent_container(self, category, initial_placement):
        assert category is not None, f"Agent Container was None"
        agent = category[0]
        category_id = agent.category
        # assert 0 <= category_id < 100, f"Category ID {category_id} should be a int between [0, 100)"
        assert (
            category_id not in self._agent_containers
        ), f"Category ID {category_id} already existed!"
        self._agent_containers[category_id] = category
        assert initial_placement in [
            "random_single",
            "direct",
        ], f"Invalid initial placement '{initial_placement}' "
        if initial_placement == "random_single":
            for agent in category:
                pos = self.find_empty_spot()
                agent.x = pos[0]
                agent.y = pos[1]
                self.add_agent(agent)
        elif initial_placement == "direct":
            for agent in category:
                self.add_agent(agent)

    def set_spot_property(self, attr_name: str, array_2d):
        """
        Extract property values from a 2d-numpy-array and assign to each spot.

        """
        assert (
            len(array_2d.shape) == 2
        ), f"The spot property array should be 2-dimensional, but got shape: {array_2d.shape}"
        assert (
            len(array_2d) == self._height
        ), f"The rows of spot property matrix is {len(array_2d)} while the height of grid is {self._height}."
        assert (
            len(array_2d[0]) == self._width
        ), f"The columns of spot property matrix is {len(array_2d[0])} while the width of grid is {self._width}."
        for y, row in enumerate(array_2d):
            for x, value in enumerate(row):
                spot = self.get_spot(x, y)
                setattr(spot, attr_name, value)

    def rand_move_agent(self, agent: GridAgent, category, range_x, range_y):
        """
        Randomly move an agent with maximum movement `range_x` in x axis and `range_y` in y axis.

        :param agent: Must be `Melodie.GridAgent`, not `Agent`. That is because `GridAgent` has predefined properties required in `Grid`.
        :param range_x: The activity range of agent on the x axis.
        :param range_y: The activity range of agent on the y axis.

        For example, if the agent is at `(0, 0)`, `range_x=1` and `range_y=0`, the result can be
        `(-1, 0), (0, 0) or (1, 0)`. The probability of these three outcomes are equal.

        :return: (int, int), the new position
        """
        source_x = agent.x
        source_y = agent.y
        self._remove_agent(agent.id, category, source_x, source_y)
        dx = floor((random() * (2 * range_x + 1))) - range_x
        dy = floor((random() * (2 * range_y + 1))) - range_y
        target_x = source_x + dx
        target_y = source_y + dy
        self._add_agent(agent.id, category, target_x, target_y)
        return self.coords_wrap(target_x, target_y)

    def get_agent_container(self, category_id) -> "AgentList":
        ret = self._agent_containers.get(category_id)
        assert (
            ret is not None
        ), f"Agent List for category id {category_id} is not registered!"
        return ret

    @property
    def agent_categories(self):
        return set(self._existed_agents.keys())


__all__ = ["GridAgent", "GridItem", "Spot", "Grid"]
