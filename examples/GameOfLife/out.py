
import time
import random
import numpy as np
from Melodie.boost.compiler.boostlib import ___agent___manager___random_sample
import numba
from numba.experimental import jitclass

_GameOfLifeSpot_ARRAY = np.zeros((0,), dtype=[('alive', 'i8'), ('role', 'i8')])
_GameOfLifeEnvironment_ARRAY = np.zeros(1, dtype=[])
@jitclass([('a', numba.int64),('al', numba.typeof(_GameOfLifeSpot_ARRAY)), ])
class Strategy():

    def __init__(self, a: int, b: 'AgentList[GameOfLifeSpot]'):
        self.a: int = a
        self.al = b

    def strategy1(self):
        return self.a

    def strategy2(self):
        return (self.a + 1)
@numba.jit
def ___agent___calc_role(___agent):
    return (1 if ___agent['alive'] else (- 1))


@numba.jit
def ___agent___update_role(___agent):
    ___agent['role']: int = ___agent___calc_role(___agent)


@numba.jit
def ___agent___alive_on_next_tick(___agent, surround_alive_count: int) -> bool:
    if ___agent['alive']:
        if ((surround_alive_count == 2) or (surround_alive_count == 3)):
            return True
        else:
            return False
    elif (surround_alive_count == 3):
        return True
    else:
        return False


@numba.jit
def ___environment___choose_strategy(___environment, al: 'AgentList[GameOfLifeSpot]'):
    strategy = Strategy(1, al)
    if (random.random() > 0.5):
        return strategy.strategy1()
    else:
        return strategy.strategy2()


@numba.jit
def ___environment___step(___environment, grid: 'Grid', al: 'AgentList[GameOfLifeSpot]'):
    buffer_status_next_tick: 'np.ndarray' = np.zeros((grid.width, grid.height), dtype=np.int64)
    for x in range(grid.width):
        for y in range(grid.height):
            neighbor_positions: 'np.ndarray' = grid.get_neighbors(x, y)
            count: int = ___environment___count_neighbor_alives(___environment, grid, neighbor_positions)
            current_spot: 'GameOfLifeSpot' = grid.get_spot(x, y)
            buffer_status_next_tick[y][x] = ___agent___alive_on_next_tick(current_spot, count)
    for x in range(grid.width):
        for y in range(grid.height):
            spot: 'GameOfLifeSpot' = grid.get_spot(x, y)
            ___agent___update_role(spot)
            if (buffer_status_next_tick[y][x] == 0):
                spot['alive'] = False
            else:
                spot['alive'] = True


@numba.jit
def ___environment___count_neighbor_alives(___environment, grid: 'Grid', neighbor_positions: 'np.ndarray'):
    alive_count = 0
    for neighbor_pos in neighbor_positions:
        spot: 'GameOfLifeSpot' = grid.get_spot(neighbor_pos[0], neighbor_pos[1])
        if spot['alive']:
            alive_count += 1
    return alive_count




def ___model___run(___model):
    ___model.visualizer.parse(___model.grid)
    ___model.visualizer.start()
    for i in range(___model.scenario.periods):
        t0: float = time.time()
        ___environment___step(___model.environment, ___model.grid, ___model.agent_list)
        t1: float = time.time()
        ___model.visualizer.parse(___model.grid)
        ___model.visualizer.step(i)
        t2: float = time.time()
        print(f'step {i}, {(t1 - t0)}s for step and {(t2 - t1)}s for conversion.')
    print(___model.grid._spots)
