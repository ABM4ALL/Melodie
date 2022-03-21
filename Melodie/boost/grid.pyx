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
from cpython.ref cimport PyObject  # somewhere at the top
from cpython cimport PyObject_GetAttr, PyObject_GetAttrString, \
    PyObject_GetItem, PyList_GetItem, PyList_Size, PyObject_SetAttr
cimport cython
from libc.math cimport pow
from libc.stdlib cimport rand, RAND_MAX
from .basics cimport Element, Agent
cimport numpy as np
import numpy as np
import time
ctypedef np.int64_t DTYPE_t
ctypedef np.float64_t DTYPE_FLOAT

ctypedef fused DTYPE_FUSED:
    np.int64_t
    np.float64_t

cdef class GridItem(Agent):
    def __init__(self, agent_id:int, x:int=0, y:int=0):
        super().__init__(agent_id)
        self.x = x
        self.y = y

    cpdef void setup(self):
        pass

    def has_attr(self, attr_name: str):
        if attr_name in {"id", "x", "y"}:
            return True
        else:
            return hasattr(self, attr_name)

    def get_attr(self, attr_name: str):
        if attr_name == "id":
            return self.id
        elif attr_name == "x":
            return self.x
        elif attr_name == "y":
            return self.y
        else:
            return self.__dict__[attr_name]

    cpdef void set_params(self, dict params) except *:
        """

        :param params:
        :return:
        """
        for paramName, paramValue in params.items():
            if paramName=='x':
                self.x = paramValue
            elif paramName=='y':
                self.y = paramValue
            elif paramName=='id':
                self.id = paramValue
            else:
                assert paramName in self.__dict__.keys(), f"param named {paramName}, value {paramValue} not in Agent.params:{self.__dict__.keys()}"
                setattr(self, paramName, paramValue)

cdef class GridAgent(GridItem):
    def __init__(self, agent_id: int, x:int=0, y:int=0):
        super().__init__(agent_id, x, y)

    cpdef void setup(self):
        pass


cdef class Spot(GridItem):
    def __init__(self, spot_id: int, x: int = 0, y: int = 0):
        super().__init__(spot_id, x, y)
        self.role = 0

    cpdef void setup(self):
        pass

cdef class Grid:
    """
    Grid is a widely-used discrete space for ABM.
    Grid contains many `Spot`s, each `Spot` could contain several agents_series_data.
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
        self._spots = [[spot_cls(self._convert_to_1d(x, y), x, y) for x in range(width)] for y in range(height)]
        for x in range(self._width):
            for y in range(self._height):
                self._spots[y][x].setup()
        self._agent_ids = {}  # [set() for i in range(width * height)]
        self._neighbors_cache = {}# [None] * self._width * self._height
        self._roles_list = [[0 for j in range(4)] for i in range(self._width*self._height)]
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
        key = (x, y, radius, moore, except_self)
        if self._neighbors_cache.get(key) is not None:
            return self._neighbors_cache[key]
        else:
            neighbors = self._neighbors(x, y, radius, moore, except_self)
            self._neighbors_cache[key] = neighbors
            return neighbors

    cdef void _add_agent(self, long agent_id, object category, long x, long y) except *:
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

        agent_id_set_list = self._get_agent_id_set_list(category)

        agent_id_set = agent_id_set_list[self._convert_to_1d(x, y)]
        if agent_id in agent_id_set:
            raise ValueError(f"Agent with id: {agent_id} already exists at position {(x, y)}!")
        else:
            agent_id_set.add(agent_id)

    cdef void _remove_agent(self, long agent_id, object category,long x, long y) except *:
        cdef dict category_of_agents
        cdef list agent_id_set_list
        cdef set agent_id_set

        x, y = self._bound_check(x, y)

        agent_id_set_list = self._get_agent_id_set_list(category)

        agent_id_set = agent_id_set_list[self._convert_to_1d(x, y)]
        if agent_id not in agent_id_set:
            print("Melodie-boost error occured. agent_id:", agent_id, "x:", x, "y:",
                  y)
            raise IndexError("agent_id does not exist on such coordinate.")
        else:
            agent_id_set.remove(agent_id)

    cpdef void add_agent(self, GridAgent agent, object category) except *:
        self._add_agent(agent.id, category, agent.x, agent.y)

    cpdef void remove_agent(self, GridAgent agent, object category) except *:
        """
        Remove agent from the grid
        :param agent_id:
        :param category:
        :return:
        """
        self._remove_agent(agent.id, category, agent.x, agent.y)

    cpdef void move_agent(self, GridAgent agent, object category, target_x, target_y) except *:
        """
        Move agent to target position.
        :param agent_id:
        :param category:
        :param target_x:
        :param target_y:
        :return:
        """
        self._remove_agent(agent.id, category, agent.x, agent.y)
        self._add_agent(agent.id, category, target_x, target_y)

    @cython.cdivision(True)
    cpdef (long, long) rand_move(self, GridAgent agent, object category, long range_x, long range_y):
        cdef long source_x, source_y, dx, dy, target_x, target_y
        source_x = agent.x
        source_y = agent.y
        self._remove_agent(agent.id, category, source_x, source_y)
        dx = <long>((rand()/(RAND_MAX*1.0))*(2*range_x+1)) - range_x
        dy = <long>((rand()/(RAND_MAX*1.0))*(2*range_y+1)) - range_y
        target_x = source_x+dx
        target_y = source_y+dy
        self._add_agent(agent.id, category, target_x, target_y)
        return target_x, target_y

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

    def get_roles_old(self):
        grid_roles = np.zeros((self._height * self._width, 4),dtype="i8")
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

    @cython.wraparound(False)
    @cython.boundscheck(False)
    cpdef tuple get_roles(self):
        cdef Spot spot
        cdef long pos_1d 
        cdef long x, y, i, j
        cdef str category_name
        cdef list category
        cdef dict agents_series_data
        cdef set agent_id_set
        cdef list role_pos_list
        cdef list _agent_ids_items_to_iterate = [(category_name, category) for category_name, category in self._agent_ids.items()]
        cdef long categories_num = len(_agent_ids_items_to_iterate)

        agents_series_data = {}
        for category_name, category in self._agent_ids.items():
            agents_series_data[category_name] = []
        for x in range(self._width):
            for y in range(self._height):
                spot = self.get_spot(x, y)
                pos_1d = self._convert_to_1d(x, y)
                role_pos_list = self._roles_list[pos_1d]
                role_pos_list[0] = x
                role_pos_list[1] = y
                role_pos_list[2] = 0
                role_pos_list[3] = spot.role
                for i in range(categories_num):
                    category_name = _agent_ids_items_to_iterate[i][0]
                    category = _agent_ids_items_to_iterate[i][1]
                    agent_id_set = category[pos_1d]
                    series_data_one_category = agents_series_data[category_name]
                    for agent_id in agent_id_set:
                        series_data_one_category.append({
                        'value': [x, y],
                        'id': agent_id,
                        'category': category_name,
                        })

        return self._roles_list, agents_series_data

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