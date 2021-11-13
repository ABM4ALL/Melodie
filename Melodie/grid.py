# Grid跟network不同，它是一张脱离agents存在的地图，上面是一个个地块，每个地块有自己的属性，其实每个地块也类似于一个agent，只不过行为上简单、被动一点儿，不乱跑。
# 在城市土地规划的例子里，每个地块可能有不同的用途规定，在模拟过程中可改变。
# 在狼、羊、草的例子里，地块上长草、被吃、再长。
# 在森林大火的例子里，地块上的植物可能被其他地块上的火引燃——所以也有互动。


# 每个spot是一个格子，很多个spot构成一个grid。
# 每个spot可以有多个属性。
# grid记录每个agent的站立的位置。

# agent和env都可以访问grid并修改：
# 1. agent的位置。
# 2. spot的属性。

# grid是run_model的可选项，如果选了，就初始化到model里
import functools
import random
import sys
import time
from typing import ClassVar, Set

import numba
import numpy as np
from numba import typeof, types
from numba.experimental import jitclass
from numba import typed

from .agent import Agent


class Spot(Agent):
    def __init__(self, spot_id: int, x: int, y: int):
        super(Spot, self).__init__(spot_id)
        self.x = x
        self.y = y

    def setup(self):
        pass


class Grid:
    def __init__(self, spot_cls: ClassVar[Spot], width: int, height: int, wrap=True):
        self.width = width
        self.height = height
        self.wrap = wrap
        self._existed_agents: Set[int] = set()
        self._spots = [[spot_cls(self._convert_to_1d(x, y), x, y) for x in range(width)] for y in range(height)]
        for x in range(self.width):
            for y in range(self.height):
                self._spots[y][x].setup()
        self._agent_ids = [set() for i in range(width * height)]

    def get_spot(self, x, y) -> "Spot":
        x, y = self._bound_check(x, y)
        return self._spots[y][x]

    def get_agent_ids(self, x: int, y: int):
        return self._agent_ids[self._convert_to_1d(x, y)]

    def _convert_to_1d(self, x, y):
        return x * self.height + y

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

    @functools.lru_cache(maxsize=100000)
    def get_neighbors(self, x, y, radius: int = 1, moore=True, except_self=True):
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
                neighbors.append((x + dx, y + dy))
        return neighbors

    def add_agent(self, agent_id: int, x: int, y: int):
        x, y = self._bound_check(x, y)
        if agent_id in self._existed_agents:
            raise ValueError(f"Agent with id: {agent_id} already exists on grid!")
        if agent_id in self._agent_ids[self._convert_to_1d(x, y)]:
            return
        else:
            self._agent_ids[self._convert_to_1d(x, y)].add(agent_id)
            self._existed_agents.add(agent_id)

    def remove_agent(self, agent_id: int, x: int, y: int):
        x, y = self._bound_check(x, y)
        if agent_id not in self._existed_agents:
            raise ValueError("Agent does not exist on the grid!")
        if agent_id not in self._agent_ids[self._convert_to_1d(x, y)]:
            print("Melodie-boost error occured. agent_id:", agent_id, "x:", x, "y:",
                  y)
            raise IndexError("agent_id does not exist on such coordinate.")
        else:
            self._agent_ids[self._convert_to_1d(x, y)].remove(agent_id)
            self._existed_agents.remove(agent_id)

    def move_agent(self, agent_id, source_x, source_y, target_x, target_y, ):
        self.remove_agent(agent_id, source_x, source_y)
        self.add_agent(agent_id, target_x, target_y)


_jit_grid_cls = None


def build_jit_class(width, height):
    global _jit_grid_cls

    # _adj = NumbaDict.empty(key_type=types.int64, value_type=types.DictType(types.int64, types.int64))
    # _nodes = NumbaDict.empty(key_type=types.int64, value_type=numba.typeof(node_elem))
    # _agents = NumbaDict.empty(key_type=types.int64, value_type=types.DictType(types.int64, types.int64))
    # _agent_pos = NumbaDict.empty(key_type=types.int64, value_type=numba.typeof(agent_elem))
    agent_num = 100
    node_num = 2000
    edge_num = 8000
    spots = np.array([[(x * height + y, x, y, random.randint(0, 1)) for x in range(width)] for y in range(height)],
                     dtype=[('id', "i8"), ('x', 'i8'), ('y', 'i8'), ("alive", "i8")])

    agent_ids = typed.List()  # .empty_list(types.ListType)
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
        ('_spots', numba.typeof(spots)),
        ('_agent_ids', numba.typeof(agent_ids)),
        ('_existed_agents', types.DictType(types.int64, types.int64))
    ])
    class GridJIT:
        def __init__(self, spots_array, agent_id_list, wrap: bool = True):
            self.wrap = wrap
            self.width = width
            self.height = height
            self._spots = spots_array
            self._agent_ids = agent_id_list
            self._existed_agents = typed.Dict.empty(types.int64, types.int64)

        def get_spot(self, x, y):
            x, y = self._bound_check(x, y)
            return self._spots[y][x]

        def get_agent_ids(self, x: int, y: int):
            return self._agent_ids[self._convert_to_1d(x, y)]

        def _convert_to_1d(self, x, y):
            return x * self.height + y

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

                    neighbors[index][0] = x + dx
                    neighbors[index][1] = y + dy
                    index += 1

            return neighbors

        def add_agent(self, agent_id: int, x: int, y: int):
            x, y = self._bound_check(x, y)
            if self._existed_agents.get(agent_id) is not None:
                raise ValueError("Agent already existed!")
            for agent_id_existed in self._agent_ids[self._convert_to_1d(x, y)]:
                if agent_id_existed == agent_id:
                    return
            self._existed_agents[agent_id] = 0
            self._agent_ids[self._convert_to_1d(x, y)].append(agent_id)

        def remove_agent(self, agent_id: int, x: int, y: int):
            x, y = self._bound_check(x, y)
            if self._existed_agents.get(agent_id) is None:
                raise ValueError("Agent does not exist on the grid!")
            exist = False
            for agent_id_existed in self._agent_ids[self._convert_to_1d(x, y)]:
                if agent_id_existed == agent_id:
                    exist = True
                    break
            if not exist:
                print("Melodie-boost error occured. agent_id:", agent_id, "x:", x, "y:",
                      y)
                raise IndexError("agent_id does not exist on such coordinate.")
            self._agent_ids[self._convert_to_1d(x, y)].remove(agent_id_existed)
            self._existed_agents.pop(agent_id)

        def move_agent(self, agent_id, source_x, source_y, target_x, target_y, ):
            self.remove_agent(agent_id, source_x, source_y)
            self.add_agent(agent_id, target_x, target_y)
            pass

    _jit_grid_cls = GridJIT
    return _jit_grid_cls(spots, agent_ids)


if __name__ == "__main__":
    grid = Grid(Spot, 10, 10)
    jit_grid = build_jit_class(10, 10)
    N = 100_000


    @numba.njit
    def jitrun(g):
        spot = None
        for i in range(N):
            neighbor_positions = g.get_neighbors(1, 1)
            for neighbor_pos in neighbor_positions:
                spot = g.get_spot(neighbor_pos[0], neighbor_pos[1])
        return spot


    def normal(g):
        for i in range(N):
            neighbor_positions = g.get_neighbors(1, 1)
            for neighbor_pos in neighbor_positions:
                spot = g.get_spot(neighbor_pos[0], neighbor_pos[1])


    jitrun(jit_grid)
    t0 = time.time()
    jitrun(jit_grid)
    t1 = time.time()
    normal(grid)
    t2 = time.time()
    print(f'jit:{t1 - t0},normal:{t2 - t1}, jit could speed up: {(t2 - t1) / (t1 - t0)} times')
