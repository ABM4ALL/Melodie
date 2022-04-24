# -*- coding:utf-8 -*-
# @Time: 2022/4/9 9:46
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: new_trainer.py.py
from Melodie.algorithms.trainer_algorithm import TrainerAlgorithm
from config import config
from model.scenario import TechnologySearchScenario
from model.model import TechnologySearchModel
from model.dataframe_loader import TechnologySearchDataFrameLoader


class NewScenario(TechnologySearchScenario):
    def setup(self):
        super().setup()
        self.cost_exploitation = 1000.0
        self.cost_exploration = 1000.0


chroms = 20
ta = TrainerAlgorithm(config, NewScenario, TechnologySearchModel, TechnologySearchDataFrameLoader)
ta.target_fcn = lambda agent: -agent.account

ta.add_agent_container('agent_list', 0, ['strategy_param_1', 'strategy_param_2', 'strategy_param_3'],
                       [i for i in range(50)])
ta.run()
