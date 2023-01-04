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
    def __init__(self, agent_id:int, grid, x:int=0, y:int=0 ):
        super().__init__(agent_id)
        self.grid = grid
        self.x = x
        self.y = y

    cpdef void set_params(self, dict params) except *:
        """

        :param params:
        :return:
        """
        for paramName, paramValue in params.items():
            assert hasattr(self, paramName), f"property named {paramName} not in {self.__class__.__name__}"
            setattr(self, paramName, paramValue)

    def __repr__(self):
        return f"<{self.__class__.__name__} 'x': {self.x}, 'y': {self.y}>"

cdef class GridAgent(GridItem):
    def __init__(self, agent_id: int, x: int = 0, y: int = 0, grid = None):
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
    def __init__(self, spot_id: int, grid: Grid, x: int = 0, y: int = 0):
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


cdef class AgentIDManager:
    def __init__(self, long width, long height, bint allow_multi=False):
        self._agents = [set() for i in range(width*height)]
        self._width = width
        self._height = height
        self._max_id = 1000000
        self.allow_multi = allow_multi
        self._empty_spots = set()
        self.all_categories = set()
        for x in range(self._width):
            for y in range(self._height):
                self._empty_spots.insert(self._convert_to_1d(x, y))

    cpdef add_agent(self, long agent_id, long category, long x, long y) except *:
        self._add_agent(agent_id, category, x, y)

    cdef void _add_agent(self, long agent_id, long category, long x, long y) except *:
        cdef long pos_1d = self._convert_to_1d(x, y)
        cdef cpp_set[long]* agents_on_spot = &self._agents[pos_1d]
        cdef long agent_num_repr = self.agent_id_and_category_to_number(agent_id, category)
        if (not self.allow_multi) and (agents_on_spot.count(pos_1d)!=0):  # If not allow multi, the spot should be empty before adding an agent.
            raise ValueError(f"Multiple agents on one spot is not allowed.")
        if agents_on_spot.count(agent_num_repr)!=0:
            raise ValueError(f"Agent id {agent_id}, category {category} already on spot <{x}, {y}>")
        
        self._empty_spots.erase(pos_1d)
        agents_on_spot.insert(agent_num_repr)
        self.all_categories.insert(category)
    
    cpdef remove_agent(self, long agent_id, long category, long x, long y) except *:
        self._remove_agent(agent_id, category, x, y)

    cdef void _remove_agent(self, long agent_id, long category, long x, long y) except *:
        cdef long pos_1d = self._convert_to_1d(x, y)
        cdef cpp_set[long]* agents_on_spot = &self._agents[pos_1d]
        cdef long agent_num_repr = self.agent_id_and_category_to_number(agent_id, category)
        if agents_on_spot.count(agent_num_repr)==0:
            raise ValueError(f"Agent id {agent_id}, category {category} does not exist on spot <{x}, {y}>")
        agents_on_spot.erase(agent_num_repr)
        if agents_on_spot.size()==0:
            self._empty_spots.insert(pos_1d)

    cdef long _convert_to_1d(self, long x, long y):
        return x * self._height + y

    cdef cpp_set[long]* _get_empty_spots(self):
        return &self._empty_spots

    cpdef set get_empty_spots(self):
        return self._empty_spots

    cpdef long agent_id_and_category_to_number(self, long agent_id, long category) except *:
        if not 0<=agent_id<=self._max_id:
            raise ValueError(f"Agent id {agent_id} out of range!")
        return category*self._max_id + agent_id

    @cython.cdivision(True)
    cpdef (long, long) number_to_category_and_agent_id(self, long num) except *:
        """
        return: (agent_id, category_id)
        """
        return num/self._max_id, num%self._max_id

    @cython.cdivision(True)
    cdef (long, long) num_to_2d_coor(self, long num) except *:
        return num/self._height, num%self._width

    cpdef list agents_on_spot(self, long x, long y) except *:
        cdef list l = []
        cdef long spot = 0
        for spot in self._agents[self._convert_to_1d(x, y)]:
            l.append(self.number_to_category_and_agent_id(spot))
        return l

    cdef (long, long) find_empty_spot(self) except *:
        cdef long rand_value = random.randint(0, self._empty_spots.size()-1)
        cdef long i = 0
        for item in self._empty_spots:
            if i==rand_value:
                return self.num_to_2d_coor(item)
            i+=1


cdef class Grid:
    """
    Grid is a widely-used discrete space for ABM. It contains many ``Spot``s,
    and agents move and interact inside spots.
    """

    def __init__(self, spot_cls: Type[Spot], scenario=None):
        """

        :param spot_cls: The class of Spot
        :param width: The width of Grid
        :param height: The height of Grid
        :param wrap: If true, the coordinate overflow will be mapped to another end.
        :param caching: If true, the neighbors and bound check results will be cached to avoid re-computing.

        """
        self.scenario = scenario
        self._spot_cls = spot_cls
        self._width = -1
        self._height = -1
        self._wrap = True
        self._multi = False
        self._caching = True

    def init_grid(self):
        """
        Initialize the grid.

        :return: None
        """
        self._spots = [[self._spot_cls(self._convert_to_1d(x, y), self, x, y) for x in range(self._width)] for y in range(self._height)]
        for x in range(self._width):
            for y in range(self._height):
                self._spots[y][x].setup()

        self._neighbors_cache = {}
        self._roles_list = [[0 for j in range(4)] for i in range(self._width*self._height)]
        self._agent_id_mgr = AgentIDManager(self._width, self._height, allow_multi=self._multi)
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
        return self._agent_id_mgr.agents_on_spot(spot.x, spot.y)


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
        self._agent_id_mgr._add_agent(agent_id, category, x, y)

    cdef void _remove_agent(self, long agent_id, long category,long x, long y) except *:
        x, y = self._bound_check(x, y)
        self._agent_id_mgr._remove_agent(agent_id, category, x, y)

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
        for category_id in self._agent_id_mgr.all_categories:
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
                for agent_category, agent_id in self._agent_id_mgr.agents_on_spot(x, y):
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
        return self._agent_id_mgr.find_empty_spot()

    cpdef list get_empty_spots(self) except *:
        """
        Get all empty spots from grid.

        :return: a list of empty spot coordinates.
        """
        cdef list positions = []
        for spot_pos_1d in self._agent_id_mgr.get_empty_spots():
            positions.append(self._agent_id_mgr.num_to_2d_coor(spot_pos_1d))
        return positions