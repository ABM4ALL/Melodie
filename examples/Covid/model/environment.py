import random

from typing import Type, List, TYPE_CHECKING
from Melodie import Environment, AgentList, Grid
from .agent import CovidAgent
from .scenario import CovidScenario


class CovidEnvironment(Environment):
    scenario: CovidScenario

    def setup(self):
        self.grid_x_size: int = self.scenario.grid_x_size
        self.grid_y_size: int = self.scenario.grid_y_size
        self.infection_probability: float = self.scenario.infection_probability
        self.accumulated_infection: int = 0

    # grid和network也应该是environment的对象，
    # 1. 概念上更清晰
    # 2. 算的一些macro variable可以被data_collector收集起来（暂时不考虑记录每个spot/node的数据）

    def setup_grid(self):
        # grid的作用
        # 1. 提供一组常用函数，比如返回邻居什么的 --> agent的坐标自动对应到spot上
        # 2. 必要的话接入丰富的背景，比如街道、桥梁，比如草原及其生长规律
        # 3. 给spot添加坐标以外的属性，可以让agent和environment改动，比如草及其长度

        # 在这个例子里grid的作用
        # 1. 常用函数
        # 2. 加入“聚集点”，考虑人口分布

        # self.grid = Grid()
        pass

    def setup_network(self):
        # network的作用
        # 1. 记录agent之间的“关系”，包括方向、强弱等 --> node就是agent，edge有可定义的属性？
        # 2. 提供一组常用函数，比如计算度什么的
        # 3. 初始化agent之间的网络结构，同一张网络可以连接不同类agent

        # 在这个例子里network的作用
        # 1. 记录传染链条
        pass

    def agents_move(self, agent_list: 'AgentList[CovidAgent]', grid: 'Grid') -> None:
        for agent in agent_list:
            agent.move(grid)

    def agents_infection(self, agent_list: 'AgentList[CovidAgent]', grid: "Grid") -> None:
        for agent in agent_list:
            neighbors = grid.get_neighbors(agent.x_pos, agent.y_pos, 1, except_self=False)
            if agent.condition == 0:
                # 从用grid返回附近agent列表，如果其中有已经感染的，则按照self.infection_probability感染
                infected: int = self.infect_from_neighbor(agent.id, neighbors, grid, agent_list)
                if infected == 1:
                    agent.condition = infected
                    self.accumulated_infection += 1
            else:
                pass

    def infect_from_neighbor(self, current_agent_id: int, neighbors: List[int], grid: 'Grid',
                             agent_list: "AgentList[CovidAgent]") -> int:
        for neighbor in neighbors:
            agent_ids = grid.get_agent_ids('agent_list', neighbor[0], neighbor[1])
            for agent_id in agent_ids:
                if agent_id == current_agent_id:
                    continue
                if agent_list[agent_id].condition == 1 and random.uniform(0, 1) < self.infection_probability:
                    return 1
        return 0
