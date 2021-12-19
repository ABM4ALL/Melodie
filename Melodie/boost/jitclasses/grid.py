# -*- coding:utf-8 -*-
# @Time: 2021/11/28 10:19
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: grid.py
import random
from typing import List, Tuple, ClassVar, TYPE_CHECKING

import numba
import numpy as np
from numba import types
from numba.experimental import jitclass
from numba import typed

from .utils import dtype_detect

if TYPE_CHECKING:
    from Melodie import Spot

_jit_grid_cls = None


def create_spots(spot_cls: ClassVar['Spot'], width: int, height: int):
    # spot = spot_cls(0, 0, 0)
    # spot.setup()
    #
    # dtypes: List[Tuple[str, str]] = []
    # user_defined_spot_attr_names: List[str] = []
    # for attr_name, attr_value in spot.__dict__.items():
    #     user_defined_spot_attr_names.append(attr_name)
    #     if isinstance(attr_value, (int, bool)):
    #         dtypes.append((attr_name, 'i8'))
    #     elif isinstance(attr_value, float):
    #         dtypes.append((attr_name, 'f8'))
    #     else:
    #         raise f'Unsupported Spot attribute "{attr_name}" with value {attr_value} '
    dtypes = dtype_detect(spot_cls, (0, 0, 0))
    spots = np.zeros((height, width), dtype=dtypes)
    for y in range(height):
        for x in range(width):
            spot = spot_cls(x * height + y, x, y)
            spot.setup()
            spots[y][x]['id'] = x * height + y
            spots[y][x]['x'] = x
            spots[y][x]['y'] = y
            for attr_name, _ in dtypes:
                spots[y][x][attr_name] = getattr(spot, attr_name)

    return spots


def JITGrid(width: int, height: int, spot_cls: ClassVar['Spot'], wrap=True):
    global _jit_grid_cls

    spots = create_spots(spot_cls, width, height)
    agent_ids = typed.List()
    for i in range(width):
        for j in range(height):
            sub_ids = typed.List.empty_list(types.int64)
            agent_ids.append(sub_ids)

    if _jit_grid_cls is not None:
        return _jit_grid_cls(spots, agent_ids)

    @jitclass([
        ('wrap', numba.typeof(True)),
        ('width', numba.typeof(1)),
        ('height', numba.typeof(1)),
        ('_category_ptr', numba.typeof(0)),
        ('_spots', numba.typeof(spots)),
        # A list of agent ids on each spot.
        # 每一个Spot包含的Agent的ID的列表
        ('_agent_ids', numba.typeof(agent_ids)),
        ('_existed_agents', types.DictType(types.unicode_type, types.DictType(types.int64, types.int64))),
        ('_all_categories', types.DictType(types.unicode_type, types.int64))
    ])
    class GridJIT:
        def __init__(self, spots_array, agent_id_list):
            self._category_ptr = 1  # from default
            self.wrap = wrap
            self.width = width
            self.height = height
            self._spots = spots_array

            # agent_ids长度为width*height的整倍数，用来存储从1~n个category中的agent
            # 取相应category时，先将二维坐标转为一维，然后加上相应系列序号的偏移。
            # 这个地方应当可以进行优化！

            self._agent_ids = agent_id_list

            self._existed_agents = typed.Dict.empty(types.unicode_type, typed.Dict.empty(types.int64, types.int64))
            self._all_categories = typed.Dict.empty(types.unicode_type, types.int64)

        def add_category(self, category_name: str):
            self._all_categories[category_name] = self._category_ptr
            self._category_ptr += 1
            self._existed_agents[category_name] = typed.Dict.empty(types.int64, types.int64)
            for i in range(width):
                for j in range(height):
                    sub_ids = typed.List.empty_list(types.int64)
                    self._agent_ids.append(sub_ids)

        def get_spot(self, x, y):
            x, y = self._bound_check(x, y)
            return self._spots[y][x]

        def get_agent_ids(self, category: str, x: int, y: int):
            index_1d = self._convert_to_1d_with_category(x, y, category)
            return self._agent_ids[index_1d]

        def _convert_to_1d(self, x, y):
            return x * self.height + y

        def _convert_index_to_2d(self, index_1d: int):
            return index_1d // self.height, index_1d % self.height

        def _convert_to_1d_with_category(self, x, y, category: str):
            return self._convert_to_1d(x, y) + self._all_categories[category] * self.width * self.height

        def _category_check(self, category_name: str):
            if self._existed_agents.get(category_name) is None:
                raise ValueError("Category name is not registered")

        def _in_bounds(self, x, y):
            return (0 <= x < self.width) and (0 <= y <= self.height)

        def _bound_check(self, x, y):
            if self.wrap:
                return self.coords_wrap(x, y)
            if not (0 <= x < self.width):
                raise IndexError("grid index x was out of range")
            elif not (0 <= y <= self.height):
                raise IndexError("grid index y was out of range")
            else:
                return x, y

        def coords_wrap(self, x, y):
            return x % self.width, y % self.height

        def get_neighbors(self, x, y, radius: int = 1, moore=True, except_self=True):
            """


            Using fix-sized numpy ndarray can be a lot (about 3 times) faster than using numba List.

            :param x:
            :param y:
            :param radius:
            :param moore:
            :param except_self:
            :return:
            """
            x, y = self._bound_check(x, y)

            length = 0
            if moore:
                length = (radius * 2 + 1) ** 2
            else:
                length = 2 * radius * (radius + 1) + 1
            if except_self:
                length -= 1

            # pre-allocate memory by creating an empty array
            neighbors = np.zeros((length, 2), dtype=np.int64)

            if not moore:
                raise NotImplementedError
            index = 0
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if not moore and abs(dx) + abs(dy) > radius:
                        continue
                    if not self.wrap and not self._in_bounds(x + dx, y + dy):
                        continue
                    if dx == 0 and dy == 0 and except_self:
                        continue
                    coor_x, coor_y = self._bound_check(x + dx, y + dy)
                    neighbors[index][0] = coor_x
                    neighbors[index][1] = coor_y
                    index += 1

            return neighbors

        def add_agent(self, agent_id: int, category: str, x: int, y: int):
            x, y = self._bound_check(x, y)

            category_dict = self._existed_agents.get(category)
            if category_dict is None:
                raise ValueError("Agent category not found!")
            if category_dict.get(agent_id) is not None:
                raise KeyError('Agent with same id already existed!')
            category_dict[agent_id] = self._convert_to_1d(x, y)

            agent_list_on_spot = self._agent_ids[self._convert_to_1d_with_category(x, y, category)]
            for agent_id_existed in agent_list_on_spot:
                if agent_id_existed == agent_id:
                    raise ValueError('Agent already on this spot!')
            agent_list_on_spot.append(agent_id)

        def _remove_agent(self, agent_id: int, category: str, x: int, y: int):
            x, y = self._bound_check(x, y)

            category_dict = self._existed_agents.get(category)
            if category_dict is None:
                raise KeyError("Agent category not found!")
            if category_dict.get(agent_id) is None:
                raise KeyError('Agent with same id does not exist!')
            category_dict.pop(agent_id)

            agent_list_on_spot = self._agent_ids[self._convert_to_1d_with_category(x, y, category)]

            exist = False
            for agent_id_existed in agent_list_on_spot:
                if agent_id_existed == agent_id:
                    exist = True
                    break
            if not exist:
                print("Melodie-boost error occured. agent_id:", agent_id, "x:", x, "y:",
                      y)
                raise IndexError("agent_id does not exist on such coordinate.")
            agent_list_on_spot.remove(agent_id_existed)

        def remove_agent(self, agent_id: int, category: str):
            """
            Remove agent from the grid
            :param agent_id:
            :param category:
            :return:
            """
            source_x, source_y = self.get_agent_pos(agent_id, category)
            self._remove_agent(agent_id, category, source_x, source_y)

        def move_agent(self, agent_id, category: str, target_x, target_y, ):
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

        def get_agent_pos(self, agent_id: int, category: str):
            index_1d = self._existed_agents[category][agent_id]
            return self._convert_index_to_2d(index_1d)

        def get_2d_array(self, layer: str = 'spots', copy: bool = True):
            arr: np.ndarray = None
            if layer == 'spots':
                arr = self._spots
            else:
                raise NotImplementedError
            if copy:
                return arr.copy()
            else:
                return arr

    _jit_grid_cls = GridJIT
    return _jit_grid_cls(spots, agent_ids)
