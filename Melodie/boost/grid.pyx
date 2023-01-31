# cython:language_level=3
# distutils: language = c++
# cython: profile=False
# -*- coding:utf-8 -*-

cdef extern from "Python.h":
    const char* PyUnicode_AsUTF8(object unicode)

import functools
from typing import Type, Set, Dict, List, Tuple
from Melodie.boost.vectorize import vectorize_2d

from cpython.ref cimport PyObject
from cpython cimport PyObject_GetAttr, PyObject_GetAttrString, \
    PyObject_GetItem, PyList_GetItem, PyList_Size, PyObject_SetAttr
cimport cython
from libc.math cimport pow
from libc.stdlib cimport rand, RAND_MAX
from libcpp.vector cimport vector
from libcpp.unordered_set  cimport unordered_set as cpp_set
from libcpp.unordered_map cimport unordered_map as cpp_map
from libcpp.string cimport string as cpp_string
from libcpp.pair cimport pair as cpp_pair
from cython.operator cimport dereference as deref, preincrement as inc

from .basics cimport Element, Agent
from .agent_list cimport AgentList
from .fastrand cimport randint
cimport numpy as np
import random
import numpy as np
import time
ctypedef np.int64_t DTYPE_t
ctypedef np.float64_t DTYPE_FLOAT

ctypedef fused DTYPE_FUSED:
    np.int64_t
    np.float64_t

cdef class GridItem(Agent):
    """
    Base class for GridAgent and Spot, an agent with x and y coordinate.
    """
    def __init__(self, agent_id:int, grid, x:int=0, y:int=0 ):
        """
        :param agent_id: ID of ``GridItem``, should be unique for same class.
        :param grid: The instance of ``Grid`` that this ``GridItem`` on.
        :param x: X coordinate on grid, an ``int``.
        :param y: Y coordinate on grid, an ``int``.
        """
        super().__init__(agent_id)
        self.grid = grid
        self.x = x
        self.y = y

    cpdef void set_params(self, dict params) except *:
        """

        :param params: Extract parameters from a dict, and assign values to properties.
        :return:
        """
        for paramName, paramValue in params.items():
            assert hasattr(self, paramName), f"property named {paramName} not in {self.__class__.__name__}"
            setattr(self, paramName, paramValue)

    def __repr__(self):
        return f"<{self.__class__.__name__} 'x': {self.x}, 'y': {self.y}>"

cdef class GridAgent(GridItem):
    """
    Base class for custom agents on grid. Different classes of custom ``GridAgent`` should
    have different value of ``category``.
    """
    def __init__(self, agent_id: int, x: int = 0, y: int = 0, grid = None):
        """
        :param agent_id: ID of ``GridAgent``, should be unique for same class.
        :param grid: The instance of ``Grid`` that this ``GridItem`` on.
        :param x: X coordinate on grid, an ``int``.
        :param y: Y coordinate on grid, an ``int``.
        """
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

    cpdef rand_move_agent(self, int x_range, int y_range) except *:
        """
        Randomly move to a new position within x and y range.

        :return: None
        """
        if self.grid is None:
            raise ValueError("Grid Agent has not been registered onto the grid!")
        self.x, self.y = self.grid.rand_move_agent(self, self.category, x_range, y_range)

cdef class Spot(GridItem):
    """
    Base class for spots.
    """
    def __init__(self, spot_id: int, grid: Grid, x: int = 0, y: int = 0):
        """
        :param spot_id: ID of ``Spot``, should be unique for same class.
        :param grid: The instance of ``Grid`` that this ``GridItem`` on.
        :param x: X coordinate on grid, an ``int``.
        :param y: Y coordinate on grid, an ``int``.
        """
        super().__init__(spot_id, grid, x, y)
        self.grid = grid
        self.colormap = 0

    def get_spot_agents(self):
        """
        Get all agents on the spot.

        :return: a list of grid agent.
        """
        return self.grid.get_spot_agents(self)

    def __repr__(self):
        return f"<{self.__class__.__name__} 'x': {self.x}, 'y': {self.y}, 'colormap': {self.colormap}, 'payload' : {self.__dict__}>"

    def get_style(self):
        return {
            "backgroundColor": "#ffffff"
        }

cdef class Grid:
    """
    Grid is a widely-used discrete space for ABM. It contains many ``Spot``s,
    and agents move and interact inside spots.
    """

    def __init__(self, spot_cls: Type[Spot], scenario=None):
        """

        :param spot_cls: The class of Spot.
        :scenario: Current scenario of grid.

        """
        self.scenario = scenario
        self._spot_cls = spot_cls
        self._width = -1
        self._height = -1
        self._wrap = True
        self._multi = False
        self._caching = True
        self._existed_agents = {}
        self._agent_ids = {}
        self._empty_spots = set()

    def init_grid(self):
        """
        Initialize the grid.

        :return: None
        """
        self._spots = [[self._spot_cls(self._convert_to_1d(x, y), self, x, y) for x in range(self._width)] for y in range(self._height)]
        
        self._empty_spots = set()
        for x in range(self._width):
            for y in range(self._height):
                spot = self._spots[y][x]
                spot.setup()
                self._empty_spots.add(self._convert_to_1d(x, y))
        self._neighbors_cache = {}
        self._roles_list = [[0 for j in range(4)] for i in range(self._width*self._height)]
        # self._agent_id_mgr = AgentIDManager(self._width, self._height, allow_multi=self._multi)
        self._agent_containers = [None for i in range(100)]
        self._agent_categories = set()
        

    def setup_params(self, width: int, height: int, wrap=True, caching=True, multi=True):
        """
        Setup the parameters of grid.

        :param width: int
        :param height: int
        :param wrap: bool, True by default.
        If True, GridAgent will re-enter the grid on the other side if it moves out of the grid on one side.
        :param caching: bool, True by default. If true, the grid caches the neighbor of each spot.
        :param multi: bool, True by default. If true, more than one agent could stand on one spot. If false, error will
        be raised when attempting to place multiple agents on one spot.
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

    @property
    def get_agent_categories(self):
        return self._agent_categories

    def setup_agent_locations(self, category ,initial_placement = "direct")->None:
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

    cpdef _add_agent_container(self, object category, str initial_placement) except *:
        cdef GridAgent agent
        cdef tuple pos
        assert category is not None, f"Agent Container was None"
        agent = category[0]
        category_id = agent.category
        assert 0<=category_id<100, f"Category ID {category_id} should be a int between [0, 100)"
        assert self._agent_containers[category_id] is None, f"Category ID {category_id} already existed!"
        self._agent_containers[category_id] = category
        self._agent_categories.add(category_id)
        assert initial_placement in {"random_single", "direct"}, f"Invalid initial placement '{initial_placement}' "
        if initial_placement == "random_single":
            for agent in category:
                pos = self.find_empty_spot()
                agent.x = pos[0]
                agent.y = pos[1]
                self.add_agent(agent)
        elif initial_placement == "direct":
            for agent in category:
                self.add_agent(agent)

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
            raise KeyError(f'Category {category} not registered!')
        return agent_ids

    cpdef Spot get_spot(self, long x, long y):
        """
        Get a ``Spot`` at position ``(x, y)``

        :param x:
        :param y:
        :return: The ``Spot`` at position (x, y)
        """
        cdef list row
        x, y = self._bound_check(x, y)
        
        row = <list>PyList_GetItem(self._spots, <Py_ssize_t> (y))
        return <Spot>PyList_GetItem(row, <Py_ssize_t> (x))

    cpdef list get_spot_agents(self, Spot spot) except *:
        """
        Get all agent of a specific category from the spot at ``(x, y)``

        :param category: category name of agent.
        :param x: 
        :param y:
        :return: A set of int, the agent ids.
        """
        return self._get_spot_agents(spot.id)

    cdef list _get_spot_agents(self, long spot_id) except *:
        """
        Get all agent of a specific category from the spot at ``(x, y)``

        :param category: category name of agent.
        :param x: 
        :param y:
        :return: A set of int, the agent ids.
        """
        l = []
        for item in self._agent_ids.items():
            category, spot_set_list = item
            for agent_id in spot_set_list[spot_id]:
                l.append((category, agent_id))
        return l


    cpdef AgentList get_agent_container(self, category_id) except *:
        cdef AgentList ret = self._agent_containers[category_id]
        assert ret is not None, f"Agent List for category id {category_id} is not registered!"
        return ret

    cdef long _convert_to_1d(self, long x, long y):
        return x * self._height + y

    cdef bint _in_bounds(self, long x, long y):
        return (0 <= x < self._width) and (0 <= y <= self._height)

    cpdef list _get_agent_id_set_list(self, object category_name):
        """
        Get category of agents_series_data
        """
        cdef list category
        category = self._agent_ids.get(category_name)
        if category is None:
            raise ValueError(f"Category {category_name} is not registered!")
        return category

    @cython.initializedcheck(False)
    cdef (long, long) _bound_check(self, long x, long y) except *:
        if self._wrap:
            return self._coords_wrap(x, y)
        if not (0 <= x < self._width):
            raise IndexError("grid index x was out of range")
        elif not (0 <= y <= self._height):
            raise IndexError("grid index y was out of range")
        else:
            return x, y

    @cython.cdivision(True)
    cdef (long, long) _coords_wrap(self, long x ,long y):
        """
        Wrap the coordination
        :param x:
        :param y:
        :return:
        """
        cdef long rem_x, rem_y
        rem_x = x % self._width
        rem_y = y % self._height 
        if rem_x < 0:
            rem_x += self._width
        if rem_y < 0:
            rem_y += self._height
        return rem_x, rem_y

    cpdef (long, long) coords_wrap(self, long x, long y):
        return self._coords_wrap(x, y)

    cdef long _get_neighbors_array_length(self, long radius, bint moore, bint except_self):
        cdef long length 
        length = 0
        if moore:
            length = (radius * 2 + 1) ** 2
        else:
            length = 2 * radius * (radius + 1) + 1
        if except_self:
            length -= 1
        return length
        
    cdef long _get_neighbors_key_hash(self, long x, long y, long radius, bint moore, bint except_self):
        """
        The key hash is:
        """
        cdef long ret
        ret =  x*2**22 
        ret += y*2**12
        ret += radius*2**3
        ret += (<long>moore)*2 + <long>except_self
        return ret

    cdef list _neighbors(self, long x, long y, long radius, bint moore, bint except_self):
        cdef long dx, dy, length, coor_x, coor_y, counter
        cdef list neighbors
        
        x, y = self._bound_check(x, y)
        length = self._get_neighbors_array_length(radius, moore, except_self)
        neighbors = [None]*length
        counter = 0
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if not moore and abs(dx) + abs(dy) > radius:
                    continue
                if not self._wrap and not self._in_bounds(x + dx, y + dy):
                    continue
                if dx == 0 and dy == 0 and except_self:
                    continue
                neighbors[counter] = self._bound_check(x + dx, y + dy)
                counter += 1
        return neighbors

    cpdef list _get_neighbor_positions(self, long x, long y, long radius = 1, bint moore=True, bint except_self=True):
        cdef list neighbors 
        cdef tuple key
        key = (x, y, radius, moore, except_self)
        if self._neighbors_cache.get(key) is not None:
            return self._neighbors_cache[key]
        else:
            neighbors = self._neighbors(x, y, radius, moore, except_self)
            self._neighbors_cache[key] = neighbors
            return neighbors

    cpdef list get_neighbors(self, GridAgent agent, long radius=1, bint moore=True, bint except_self=True) except *:
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
        neighbor_positions = self._get_neighbor_positions(agent.x, agent.y, radius, moore, except_self)
        for neighbor_pos in neighbor_positions:
            x, y = neighbor_pos
            agent_ids = self.get_spot_agents(
                self.get_spot(x, y)
            )  
            neighbor_ids.extend(agent_ids)
        return neighbor_ids
    
    def _get_neighborhood(self, x, y, radius = 1, moore=True, except_self=True):
        """
        Get all spots around (x, y)

        """
        neighbor_positions = self._get_neighbor_positions(x, y, radius, moore, except_self)
        spots = []
        for pos in neighbor_positions:
            x, y = pos
            spots.append(self.get_spot(x, y))
        return spots

    def get_agent_neighborhood(self, agent, radius = 1, moore=True, except_self=True):
        return self._get_neighborhood(agent.x, agent.y, radius, moore, except_self)

    def get_spot_neighborhood(self, spot, radius = 1, moore=True, except_self=True):
        return self._get_neighborhood(spot.x, spot.y, radius, moore, except_self)

    cdef void _add_agent(self, long agent_id, long category, long x, long y) except *:
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
            for _ in range(self._width*self._height):
                l.append(set())
            self._agent_ids[category] = l  # = [set()
            #  for _ in range(self._width * self._height)]

        category_of_agents =  self._existed_agents[category]

        if agent_id in category_of_agents:
            raise ValueError(
                f"Agent with id: {agent_id} already exists on grid!")
        pos_1d = self._convert_to_1d(x, y)
        if agent_id in self._agent_ids[category][pos_1d]:
            raise ValueError(
                f"Agent with id: {agent_id} already exists at position {(x, y)}!")
        else:
            self._agent_ids[category][pos_1d].add(agent_id)
            self._existed_agents[category][agent_id] = (x, y)
        if pos_1d in self._empty_spots:
            self._empty_spots.remove(pos_1d)

    cdef void _remove_agent(self, long agent_id, long category,long x, long y) except *:
        x, y = self._bound_check(x, y)

        category_of_agents =  self._existed_agents[category]

        if agent_id not in category_of_agents.keys():
            raise ValueError(
                f"Agent with id: {agent_id} does not exist on grid!")
        pos_1d = self._convert_to_1d(x, y)
        if agent_id not in self._existed_agents[category]:
            raise ValueError("Agent does not exist on the grid!")
        if agent_id not in self._agent_ids[category][pos_1d]:
            print("Melodie-boost error occured. agent_id:", agent_id, "x:", x, "y:",
                  y)
            raise IndexError("agent_id does not exist on such coordinate.")
        else:
            self._agent_ids[category][pos_1d].remove(agent_id)
            self._existed_agents[category].pop(agent_id)

        agents = self._get_spot_agents(pos_1d)
        if len(agents) == 0:
            self._empty_spots.add(pos_1d)

    cpdef void add_agent(self, GridAgent agent) except *:
        """
        Add an agent to the grid

        :param agent: An GridAgent object.
        :param category: A string, the name of category. The category should be registered. 
        :return:
        """
        agent.grid = self
        self._add_agent(agent.id, agent.category, agent.x, agent.y)

    cpdef void remove_agent(self, GridAgent agent) except *:
        """
        Remove an agent from the grid

        :param agent: An GridAgent object.
        :param category: A string, the name of category. The category should be registered. 
        :return: None
        """
        agent.grid = None
        self._remove_agent(agent.id, agent.category, agent.x, agent.y)

    cpdef void move_agent(self, GridAgent agent, long target_x, long target_y) except *:
        """
        Move agent to target position.

        :param agent: An GridAgent object.
        :param category: A string, the name of category. The category should be registered. 
        :param target_x: The target x coordinate
        :param target_y: The target y coordinate
        :return: None
        """
        
        self._remove_agent(agent.id, agent.category, agent.x, agent.y)
        self._add_agent(agent.id, agent.category, target_x, target_y)
        agent.x = target_x
        agent.y = target_y

    @cython.cdivision(True)
    cpdef (long, long) rand_move_agent(self, GridAgent agent, long category, long range_x, long range_y) except *:
        """
        Randomly move an agent with maximum movement `range_x` in x axis and `range_y` in y axis.
        
        :param agent: Must be `Melodie.GridAgent`, not `Agent`. That is because `GridAgent` has predefined properties required in `Grid`. 
        :param range_x: The activity range of agent on the x axis. 
        :param range_y: The activity range of agent on the y axis.
        
        For example, if the agent is at `(0, 0)`, `range_x=1` and `range_y=0`, the result can be
        `(-1, 0), (0, 0) or (1, 0)`. The probability of these three outcomes are equal.

        :return: (int, int), the new position
        """
        cdef long source_x, source_y, dx, dy, target_x, target_y
        source_x = agent.x
        source_y = agent.y
        self._remove_agent(agent.id, category, source_x, source_y)
        dx = <long>((rand()/(RAND_MAX*1.0))*(2*range_x+1)) - range_x
        dy = <long>((rand()/(RAND_MAX*1.0))*(2*range_y+1)) - range_y
        target_x = source_x+dx
        target_y = source_y+dy
        self._add_agent(agent.id, category, target_x, target_y)
        return self._coords_wrap(target_x, target_y)

    def to_2d_array(self, attr_name: str) -> np.ndarray:
        """
        Collect property of each spot and write the property value into an 2d np.array.

        Notice:

        - The property to collect should be float/int/bool, not other types such as str.
        - If you would like to get an element from the returned array, please write like this:
        
        .. code-block:: python
            :linenos:

            arr = self.to_2d_array('some_attr')
            y = 10
            x = 5
            spot_at_x_5_y_10 = arr[y][x] # CORRECT. Get the some_attr value of spot at `x = 5, y = 10`
            spot_at_x_5_y_10 = arr[x][y] # INCORRECT. You will get the value of spot at `x = 10, y = 5`
        

        :param attr_name: the property name to collect for this model.
        :return:
        """
        return vectorize_2d(self._spots, attr_name)

    def set_spot_property(self, attr_name: str, array_2d):
        """
        Set property from an 2d-numpy-array to each spot.

        """
        assert len(array_2d.shape) == 2, f"The spot property array should be 2-dimensional, but got shape: {array_2d.shape}"
        assert len(array_2d) == self._height, f"The rows of spot property matrix is {len(array_2d)} while the height of grid is {self._height}."
        assert len(array_2d[0]) == self._width, f"The columns of spot property matrix is {len(array_2d[0])} while the width of grid is {self._width}."
        for y, row in enumerate(array_2d):
            for x, value in enumerate(row):
                spot = self.get_spot(x, y)
                setattr(spot, attr_name, value)

    cpdef tuple get_colormap(self):
        """
        Get the role of each spot.

        :return: A tuple. The first item is a nested list for spot roles, and the second item is a dict for agent roles.
        """
        cdef Spot spot
        cdef long pos_1d 
        cdef long x, y, i, j
        cdef long category_id, agent_category
        cdef list category
        cdef dict agents_series_data
        cdef set agent_id_set
        cdef list role_pos_list

        agents_series_data = {}
        for category_id in self._agent_ids.keys():
            agents_series_data[category_id] = []
        for x in range(self._width):
            for y in range(self._height):
                spot = self.get_spot(x, y)
                pos_1d = self._convert_to_1d(x, y)
                role_pos_list = self._roles_list[pos_1d]
                role_pos_list[0] = x
                role_pos_list[1] = y
                role_pos_list[2] = 0
                role_pos_list[3] = spot.colormap
                # for agent_category, agent_id in self._agent_id_mgr.agents_on_spot(x, y):
                for agent_category, agent_id in self._get_spot_agents(spot.id):
                    series_data_one_category = agents_series_data[agent_category]
                    series_data_one_category.append({
                        'value': [x, y],
                        'id': agent_id,
                        'category': agent_category,
                        })

        return self._roles_list, agents_series_data
    
    cpdef long height(self):
        """
        Get the height of grid 

        :return: height, an ``int``
        """
        return self._height
    
    cpdef long width(self):
        """
        Get the width of grid

        :return: width, an ``int``
        """
        return self._width

    cpdef (long, long) find_empty_spot(self) except *:
        """
        Get a coordinate (x, y) of a spot without any agent on it.

        :return: A tuple, (x, y)
        """
        rand_value = randint(0, len(self._empty_spots) - 1)
        i = 0
        for item in self._empty_spots:
            if i == rand_value:
                return self._num_to_2d_coor(item)
            i += 1
        return -1, -1

    cpdef list get_empty_spots(self) except *:
        """
        Get all empty spots from grid.

        :return: a list of empty spot coordinates.
        """
        cdef list positions = []
        for spot_pos_1d in self._empty_spots:
            positions.append(self._num_to_2d_coor(spot_pos_1d))
        return positions

    def _num_to_2d_coor(self, num: int):
        return num // self._height, num % self._width