# -*- coding:utf-8 -*-
# @Time: 2022/4/8 21:57
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_new_trainer_algorithm.py

# from Melodie.algorithms.trainer_algorithm import TrainerAlgorithm

from Melodie import Agent, Model, Scenario
from .config import cfg


class DemoAgent(Agent):
    def setup(self):
        self.param1 = 0.0
        self.param2 = 0.0


class NewModel(Model):
    def setup(self):
        self.agent_list = self.create_agent_container(DemoAgent, 10)


def target_fcn(agent: DemoAgent):
    return agent.param1 ** 2 + agent.param2 ** 2


def _test_chrom_params():
    chroms = 20
    ta = TrainerAlgorithm(cfg, NewModel, Scenario, )
    scenario = Scenario(0)
    # model = NewModel(cfg, scenario)

    ta.add_agent_container('agent_list', 0, ['param1', 'param2'], [i for i in range(10)])
    ta._current_model: NewModel = ta.create_model()
    al = ta._current_model.agent_list
    algorithm_at_agent_0 = ta.algorithms_dict[(0, 0)]
    # algorithm_at_agent_0.run()
    for chrom_id in range(chroms):
        chrom_value_param1, chrom_value_param2 = algorithm_at_agent_0.chrom2x(algorithm_at_agent_0.Chrom)[chrom_id]
        ta.params_from_algorithm_to_agent_container(chrom_id)
        assert al.get_agent(0).param1 == chrom_value_param1
        assert al.get_agent(0).param2 == chrom_value_param2
    # ta.target_fcn_cache.new_cache(0, 0)
    ta.target_function_from_model_to_cache(target_fcn, 0, 0)
    # ta.target_fcn_cache.end_cache()
    assert (0, 0) in ta.target_fcn_cache.target_fcn_record
    print(ta.target_fcn_cache.target_fcn_record)


def _test_chrom_params_algorithm():
    chroms = 20
    ta = TrainerAlgorithm(cfg, Scenario, NewModel, )
    ta.target_fcn = target_fcn
    scenario = Scenario(0)
    # model = NewModel(cfg, scenario)

    ta.add_agent_container('agent_list', 0, ['param1', 'param2'], [i for i in range(10)])
    ta.run()
