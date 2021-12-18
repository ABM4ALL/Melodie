
import numpy as np
from typing import Type
from Melodie import Environment, AgentList
from .agent import CovidAgent
from .scenario import CovidScenario


class CovidEnvironment(Environment):

    def setup(self):
        scenario: CovidScenario = self.current_scenario()
        self.grid_x_size = scenario.grid_x_size
        self.grid_y_size = scenario.grid_y_size
        self.infection_probability = scenario.infection_probability
        self.accumulated_infection = 0

    # grid和network也应该是environment的对象，
    # 1. 概念上更清晰
    # 2. 算的一些macro variable可以被data_collector收集起来（暂时不考虑记录每个spot/node的数据）

    def setup_gird(self):
        # grid的作用
        # 1. 提供一组常用函数，比如返回邻居什么的 --> agent的坐标自动对应到spot上
        # 2. 必要的话接入丰富的背景，比如街道、桥梁，比如草原及其生长规律
        # 3. 给spot添加坐标以外的属性，可以让agent和environment改动，比如草及其长度

        # 在这个例子里grid的作用
        # 1. 常用函数
        # 2. 加入“聚集点”，考虑人口分布
        pass

    def setup_network(self):
        # grid的作用
        # 1. 记录agent之间的“关系”，包括方向、强弱等 --> node就是agent，edge有可定义的属性？
        # 2. 提供一组常用函数，比如计算度什么的
        # 3. 初始化agent之间的网络结构，同一张网络可以连接不同类agent

        # 在这个例子里network的作用
        # 1. 记录传染链条
        pass

    def agents_move(self, agent_list: 'AgentList[CovidAgent]') -> None:
        for agent in agent_list:
            agent.move()

    def agents_infection(self, agent_list: 'AgentList[CovidAgent]') -> None:
        for agent in agent_list:
            if agent.condition == 0:
                # 从用grid返回附近agent列表，如果其中有已经感染的，则按照self.infection_probability感染
                agent.condition = 1
                self.accumulated_infection += 1
            else:
                pass
