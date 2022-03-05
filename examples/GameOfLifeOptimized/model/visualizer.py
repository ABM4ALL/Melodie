# -*- coding:utf-8 -*-
# @Time: 2021/11/12 18:51
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: run_studio.py
import random

# import numba
# import numpy as np
# from numba import typed

from Melodie.grid import Grid
from Melodie.visualizer import GridVisualizer


class GameOfLifeVisualizer(GridVisualizer):
    def setup(self):
        self.add_agent_series('sheep', 'scatter', '#bbff00', )
        self.add_agent_series('agents', 'scatter', '#bb0000', )

    def parse(self, grid):
        self.parse_series(grid)


    def parse_roles_jit(self, grid):
        # parsed = parse_with_jit(grid, spot_role_jit)
        self.grid_roles = grid.get_roles().tolist()

        other_series_data = {}
        existed_agents = grid._existed_agents
        for category in existed_agents.keys():
            if other_series_data.get(category) is None:
                other_series_data[category] = []
            for agent_id in existed_agents[category]:
                pos = grid.get_agent_pos(agent_id, category)
                # pos = existed_agents[category][agent_id]
                other_series_data[category].append({
                    'value': list(pos),
                    'id': agent_id,
                    'category': category,
                })
        for series_name, data in other_series_data.items():
            self.other_series[series_name]['data'] = data

    def other_series_data(self):
        pass
