# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from Melodie import Model
from .agent import GiniAgent
from .data_collector import GiniDataCollector
from .environment import GiniEnvironment


class GiniModel(Model):

    def setup(self):
        # 已完成
        # 让用户自己setup agent_list -->
        # self.wolf_list = self.setup_agent_list(scenario.get_registered_dataframe("wolf_params")[id_scenario == scenario.id])
        # 需要确保参数来自当前的scenario_id。这个最好melodie在后台自动实现。因为用户最好不要考虑scenario_id
        # self.sheep_list = self.setup_agent_list(scenario.get_registered_dataframe("sheep_params"))
        # 写多个agent_list，不能仅仅是一个agent_list。
        # datacollector也会跟着改变。有多个
        # 如果用户已经注册了
        self.agent_list = self.create_agent_container(GiniAgent, self.scenario.agent_num,
                                                      self.scenario.get_registered_dataframe('agent_params'))

        with self.define_basic_components():
            # 在这个with语句中，调用define_model_components()来添加environment和datacollector。
            # 这样就不用在run.py中传入相关的信息了。
            # 这样就不需要在setup方法之外（12~13行）添加类型提示语句了。
            # 在退出这个with语句的时候会进行后检查和后处理。
            # 后检查内容是：
            # 1、environment必须已经定义。如果未定义则报错
            # 2、datacollector可不定义。如果未定义也不会报错
            # 后处理内容是：
            # 1、environment一定是已经定义的，因此执行其setup()方法以及其他操作
            # 2、如果datacollector已经定义，就执行它的setup()方法以及其他操作
            self.environment = GiniEnvironment()
            self.data_collector = GiniDataCollector()


    def run(self):
        for t in range(0, self.scenario.periods):
            self.environment.go_money_produce(self.agent_list)
            self.environment.go_money_transfer(self.agent_list)
            self.environment.calc_wealth_and_gini(self.agent_list)
            self.data_collector.collect(t)
        self.data_collector.save()