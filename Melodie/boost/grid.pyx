# cython:language_level=3
# cython: profile=False
# -*- coding:utf-8 -*-
# @Time: 2021/10/3 20:58
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: grid.pyx

import functools
from typing import ClassVar, Set, Dict, List, Tuple
from Melodie.boost.vectorize import vectorize_2d
from Melodie.agent import Agent
from cpython.ref cimport PyObject  # somewhere at the top
from cpython cimport PyObject_GetAttr, PyObject_GetAttrString, \
    PyObject_GetItem, PyList_GetItem, PyList_Size, PyObject_SetAttr
cimport cython
from libc.math cimport pow
from libc.stdlib cimport rand, RAND_MAX
cimport numpy as np
import numpy as np
import time
ctypedef np.int64_t DTYPE_t
ctypedef np.float64_t DTYPE_FLOAT

ctypedef fused DTYPE_FUSED:
    np.int64_t
    np.float64_t

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef f(object testlist):
    cdef object[:, :] testarr
    cdef np.ndarray ar1
    cdef object testobj
    cdef long i, length
    ar1 = np.array(testlist, dtype=object)
    testarr = ar1
    print(testarr, ar1)
    length = len(testlist)
    t0 = time.time()
    for i in range(10000_000):
        for j in range(length):
            testobj = testlist[j][0]
    t1 = time.time()
    print("list",t1-t0)

    t0 = time.time()
    for i in range(10000_000):
        for j in range(length):
            testobj = testarr[j, 0]
    t1 = time.time()
    print("arr", t1-t0)


    pass

cdef class Spot:
    def __init__(self, spot_id: int, x: int = 0, y: int = 0):
        self.id = spot_id
        # self.scenario: Optional['Scenario'] = None
        # self.model: Optional['Model'] = None
        self.x = x
        self.y = y
        self.scenario = None
        self.model = None

    cpdef void setup(self):
        pass

cdef class Grid:
    """
    Grid is a widely-used discrete space for ABM.
    Grid contains many `Spot`s, each `Spot` could contain several agents.
    """

    def __init__(self, spot_cls: ClassVar[Spot], width, height, wrap=True, caching=True):
        """

        :param spot_cls: The class of Spot
        :param width: The width of Grid
        :param height: The height of Grid
        :param wrap: If true, the coordinate overflow will be mapped to another end.
        :param caching: If true, the neighbors and bound check results will be cached to avoid re-computing.

        """
        self._width = width
        self._height = height
        self.wrap = wrap
        self._existed_agents = {}
        self._spots = [[spot_cls(self._convert_to_1d(x, y), x, y) for x in range(width)] for y in range(height)]
        for x in range(self._width):
            for y in range(self._height):
                self._spots[y][x].setup()
        self._agent_ids = {}  # [set() for i in range(width * height)]
        self._neighbors_cache = {}# [None] * self._width * self._height
        #if caching:
        #    self.get_neighbors = functools.lru_cache(self._width * self._height)(self.get_neighbors)
        #    self._bound_check = functools.lru_cache(self._width * self._height)(self._bound_check)

    cpdef add_category(self, object category_name):
        """
        Add agent category
        :param category_name:
        :return:
        """
        self._agent_ids[category_name] = [set() for i in range(self._width * self._height)]
        self._existed_agents[category_name] = {}

    # @cython.boundscheck(False)
    # @cython.wraparound(False)
    cpdef get_spot(self, long x, long y):
        """
        Get a spot at position (x, y)
        :param x:
        :param y:
        :return:
        """
        cdef list row
        x, y = self._bound_check(x, y)
        
        row = <list>PyList_GetItem(self._spots, <Py_ssize_t> (y))
        
        # row = <list>self._spots[y]
        # return row[x]
        return <list>PyList_GetItem(row, <Py_ssize_t> (x))

    cpdef get_agent_ids(self, object category, long x, long y):
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

    cdef long _convert_to_1d(self, long x, long y):
        return x * self._height + y

    cdef bint _in_bounds(self, long x, long y):
        return (0 <= x < self._width) and (0 <= y <= self._height)

    cpdef _get_category_of_agents(self, object category_name):
        """
        Get category of agents
        """
        cdef dict category
        category = self._existed_agents.get(category_name)
        if category is None:
            raise ValueError(f"Category {category_name} is not registered!")
        return category

    @cython.initializedcheck(False)
    cdef (long, long) _bound_check(self, long x, long y):
        if self.wrap:
            return self._coords_wrap(x, y)
        if not (0 <= x < self._width):
            raise IndexError("grid index x was out of range")
        elif not (0 <= y <= self._height):
            raise IndexError("grid index y was out of range")
        else:
            return x, y

    # @cython.cdivision(True)
    cdef (long, long) _coords_wrap(self, long x ,long y):
        """
        Wrap the coordination
        :param x:
        :param y:
        :return:
        """
        return x % self._width, y % self._height

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
                if not self.wrap and not self._in_bounds(x + dx, y + dy):
                    continue
                if dx == 0 and dy == 0 and except_self:
                    continue
                # coor_x, coor_y = self._bound_check(x + dx, y + dy)
                neighbors[counter] = self._bound_check(x + dx, y + dy)
                counter += 1
        return neighbors

    cpdef list get_neighbors(self, long x, long y, long radius = 1, bint moore=True, bint except_self=True):
        """
        Get the neighbors of some spot.
        :param x:
        :param y:
        :param radius:
        :param moore:
        :param except_self:
        :return:  -> List[Tuple[int, int]]
        """
        cdef list neighbors 
        cdef tuple key
        # cdef object key
        key = (x, y, radius, moore, except_self)
        # key = self._get_neighbors_key_hash(x, y, radius, moore, except_self)
        if self._neighbors_cache.get(key) is not None:
            return self._neighbors_cache[key]
        else:
            neighbors = self._neighbors(x, y, radius, moore, except_self)
            self._neighbors_cache[key] = neighbors
            return neighbors

        # if self._neighbors_cache[self._convert_to_1d(x, y)] is not None:
        #     return self._neighbors_cache[self._convert_to_1d(x, y)]
        # else:
        #     neighbors = self._neighbors(x, y, radius, moore, except_self)
        #     self._neighbors_cache[self._convert_to_1d(x, y)] = neighbors
        #     return neighbors

    cpdef void add_agent(self, long agent_id, object category, long x, long y):
        """
        Add agent onto the grid
        :param agent_id:
        :param category:
        :param x:
        :param y:
        :return:
        """
        cdef dict category_of_agents
        cdef list agent_id_set_list
        cdef set agent_id_set
        
        x, y = self._bound_check(x, y)

        category_of_agents = self._get_category_of_agents(category)

        if agent_id in category_of_agents.keys():
            raise ValueError(f"Agent with id: {agent_id} already exists on grid!")
        agent_id_set_list = self._agent_ids[category]
        if agent_id in agent_id_set_list[self._convert_to_1d(x, y)]:
            raise ValueError(f"Agent with id: {agent_id} already exists at position {(x, y)}!")
        else:
            agent_id_set = agent_id_set_list[self._convert_to_1d(x, y)]
            agent_id_set.add(agent_id)
            category_of_agents[agent_id] = (x, y)

    cdef _remove_agent(self, long agent_id, object category,long x, long y):
        cdef dict category_of_agents
        cdef list agent_id_set_list
        cdef set agent_id_set

        x, y = self._bound_check(x, y)

        category_of_agents = self._get_category_of_agents(category)

        if agent_id not in category_of_agents:
            raise ValueError(f"Agent with id: {agent_id} does not exist on grid!")

        agent_id_set_list = self._agent_ids[category]
        agent_id_set = agent_id_set_list[self._convert_to_1d(x, y)]
        if agent_id not in agent_id_set:
            print("Melodie-boost error occured. agent_id:", agent_id, "x:", x, "y:",
                  y)
            raise IndexError("agent_id does not exist on such coordinate.")
        else:
            agent_id_set.remove(agent_id)
            self._existed_agents[category].pop(agent_id)

    def remove_agent(self, agent_id: long, category: str):
        """
        Remove agent from the grid
        :param agent_id:
        :param category:
        :return:
        """
        source_x, source_y = self.get_agent_pos(agent_id, category)
        self._remove_agent(agent_id, category, source_x, source_y)

    def move_agent(self, agent_id, category: str, target_x, target_y):
        """
        Move agent to target position.
        :param agent_id:
        :param category:
        :param target_x:
        :param target_y:
        :return:
        """
        source_x, source_y = self.get_agent_pos(agent_id, category)
        self._remove_agent(agent_id, category, source_x, source_y)
        self.add_agent(agent_id, category, target_x, target_y)

    @cython.cdivision(True)
    cpdef (long, long) rand_move(self, long agent_id, object category, long range_x, long range_y):
        cdef long source_x, source_y, dx, dy, target_x, target_y
        source_x, source_y = self.get_agent_pos(agent_id, category)
        self._remove_agent(agent_id, category, source_x, source_y)
        dx = <long>((rand()/(RAND_MAX*1.0))*(2*range_x+1)) - range_x
        dy = <long>((rand()/(RAND_MAX*1.0))*(2*range_y+1)) - range_y
        target_x = source_x+dx
        target_y = source_y+dy
        self.add_agent(agent_id, category, target_x, target_y)
        return target_x, target_y

    cpdef (long, long) get_agent_pos(self, long agent_id, object category):
        """
        Get the agent position at the grid.
        :param agent_id:
        :param category:
        :return:
        """
        return self._existed_agents[category][agent_id]

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
        grid_roles = np.zeros((self._height * self._width, 4))
        for x in range(self._width):
            for y in range(self._height):
                spot = self.get_spot(x, y)
                # role = spot.role
                pos_1d = self._convert_to_1d(x, y)
                grid_roles[pos_1d, 0] = x
                grid_roles[pos_1d, 1] = y
                grid_roles[pos_1d, 2] = 0
                grid_roles[pos_1d, 3] = spot.role
        return grid_roles

    # @property
    # def height(self):
    #     return self._height
    
    # @property
    # def width(self):
    #     return self._width
    
    cpdef long height(self):
        return self._height
    
    cpdef long width(self):
        return self._width