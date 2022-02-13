# cython:language_level=3
# -*- coding:utf-8 -*-
# @Time: 2021/10/3 20:58
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: grid.pyx

import functools
from typing import ClassVar, Set, Dict, List, Tuple
from .vectorize import vectorize_2d
from Melodie.agent import Agent
from cpython.ref cimport PyObject  # somewhere at the top
from cpython cimport PyObject_GetAttr, PyObject_GetAttrString, \
    PyObject_GetItem, PyList_GetItem, PyList_Size, PyObject_SetAttr
cimport cython
from libc.stdlib cimport rand, RAND_MAX
cimport numpy as np
import numpy as np

ctypedef np.int64_t DTYPE_t
ctypedef np.float64_t DTYPE_FLOAT

ctypedef fused DTYPE_FUSED:
    np.int64_t
    np.float64_t

class Spot(Agent):
    def __init__(self, spot_id: int, x: int = 0, y: int = 0):
        super(Spot, self).__init__(spot_id)
        self.x = x
        self.y = y

    def setup(self):
        pass

cdef class Grid:
    """
    Grid is a widely-used discrete space for ABM.
    Grid contains many `Spot`s, each `Spot` could contain several agents.
    """
    cdef int _width
    cdef int _height
    cdef bint wrap
    cdef dict _existed_agents
    cdef list _spots
    cdef dict _agent_ids

    def __init__(self, spot_cls: ClassVar[Spot], width: int, height: int, wrap=True, caching=True):
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
        self._existed_agents: Dict[str, Dict[int, Tuple[int, int]]] = {}
        self._spots = [[spot_cls(self._convert_to_1d(x, y), x, y) for x in range(width)] for y in range(height)]
        for x in range(self._width):
            for y in range(self._height):
                self._spots[y][x].setup()
        self._agent_ids: Dict[str, List[Set[int]]] = {}  # [set() for i in range(width * height)]

        #if caching:
        #    self.get_neighbors = functools.lru_cache(self._width * self._height)(self.get_neighbors)
        #    self._bound_check = functools.lru_cache(self._width * self._height)(self._bound_check)

    def add_category(self, category_name: str):
        """
        Add agent category
        :param category_name:
        :return:
        """
        self._agent_ids[category_name] = [set() for i in range(self._width * self._height)]
        self._existed_agents[category_name] = {}

    def get_spot(self, x, y) -> "Spot":
        """
        Get a spot at position (x, y)
        :param x:
        :param y:
        :return:
        """
        x, y = self._bound_check(x, y)
        return self._spots[y][x]

    def get_agent_ids(self, category: str, x: int, y: int) -> Set[int]:
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

    cdef int _convert_to_1d(self, int x, int y):
        return x * self._height + y

    cdef bint _in_bounds(self, int x, int y):
        return (0 <= x < self._width) and (0 <= y <= self._height)

    def _get_category_of_agents(self, category_name: str):
        category = self._existed_agents.get(category_name)
        if category is None:
            raise ValueError(f"Category {category_name} is not registered!")
        return category

    cdef (int, int) _bound_check(self, int x, int y):
        if self.wrap:
            return self._coords_wrap(x, y)
        if not (0 <= x < self._width):
            raise IndexError("grid index x was out of range")
        elif not (0 <= y <= self._height):
            raise IndexError("grid index y was out of range")
        else:
            return x, y

    cdef (int, int) _coords_wrap(self, int x ,int y):
        """
        Wrap the coordination
        :param x:
        :param y:
        :return:
        """
        return x % self._width, y % self._height

    def coords_wrap(self, x, y):
        return self._coords_wrap(x, y)

    cdef list _neighbors(self, int x, int y, int radius, bint moore, bint except_self):
        cdef list neighbors
        cdef int dx,dy

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

    def get_neighbors(self, int x, int y, int radius = 1, bint moore=True, bint except_self=True) -> List[Tuple[int, int]]:
        """
        Get the neighbors of some spot.
        :param x:
        :param y:
        :param radius:
        :param moore:
        :param except_self:
        :return:
        """
        return self._neighbors(x, y, radius, moore, except_self)

    def add_agent(self, agent_id: int, category: str, x: int, y: int):
        """
        Add agent onto the grid
        :param agent_id:
        :param category:
        :param x:
        :param y:
        :return:
        """
        x, y = self._bound_check(x, y)

        category_of_agents = self._get_category_of_agents(category)

        if agent_id in category_of_agents.keys():
            raise ValueError(f"Agent with id: {agent_id} already exists on grid!")

        if agent_id in self._agent_ids[category][self._convert_to_1d(x, y)]:
            raise ValueError(f"Agent with id: {agent_id} already exists at position {(x, y)}!")
        else:
            self._agent_ids[category][self._convert_to_1d(x, y)].add(agent_id)
            self._existed_agents[category][agent_id] = (x, y)

    def _remove_agent(self, agent_id: int, category: str, x: int, y: int):
        x, y = self._bound_check(x, y)

        category_of_agents = self._get_category_of_agents(category)

        if agent_id not in category_of_agents.keys():
            raise ValueError(f"Agent with id: {agent_id} does not exist on grid!")

        if agent_id not in self._existed_agents[category]:
            raise ValueError("Agent does not exist on the grid!")
        if agent_id not in self._agent_ids[category][self._convert_to_1d(x, y)]:
            print("Melodie-boost error occured. agent_id:", agent_id, "x:", x, "y:",
                  y)
            raise IndexError("agent_id does not exist on such coordinate.")
        else:
            self._agent_ids[category][self._convert_to_1d(x, y)].remove(agent_id)
            self._existed_agents[category].pop(agent_id)

    def remove_agent(self, agent_id: int, category: str):
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

    def rand_move(self, agent_id, category, range_x, range_y):
        source_x, source_y = self.get_agent_pos(agent_id, category)
        self._remove_agent(agent_id, category, source_x, source_y)
        dx = int((rand()/(RAND_MAX*1.0))*(2*range_x+1)) - range_x
        dy = int((rand()/(RAND_MAX*1.0))*(2*range_y+1)) - range_y
        target_x = source_x+dx
        target_y = source_y+dy
        self.add_agent(agent_id, category, target_x, target_y)
        return target_x, target_y

    def get_agent_pos(self, agent_id: int, category: str) -> Tuple[int, int]:
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

    @property
    def height(self):
        return self._height
    
    @property
    def width(self):
        return self._width