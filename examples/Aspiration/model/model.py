# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from Melodie import Model, AgentList
from .agent import AspirationAgent
from .environment import AspirationEnvironment
from .data_collector import AspirationDataCollector


class AspirationModel(Model):

    def setup(self):
        self.agent_list: AgentList[AspirationAgent] = self.create_agent_container(AspirationAgent,
                                                                                  self.scenario.agent_num,
                                                                                  self.scenario.get_registered_dataframe(
                                                                                      'agent_params'))
        with self.define_basic_components():
            # 在这个with语句中，调用define_model_components()来添加environment和datacollector。
            # 这样就不用在run.py中传入相关的信息了。
            # 这样就不需要在setup方法之外（12~13行）添加类型提示语句了。
            # 在退出这个with语句的时候会进行进行后检查和后处理。
            # 检查内容是：
            # 1、environment必须已经定义。如果未定义则报错
            # 2、datacollector可不定义。如果未定义也不会报错
            # 后处理内容是：
            # 1、environment一定是已经定义的，因此执行其setup()方法以及其他操作
            # 2、如果datacollector已经定义，就执行它的setup()方法以及其他操作

            self.environment = AspirationEnvironment()
            self.data_collector = AspirationDataCollector()

    def run(self):
        for t in range(0, self.scenario.periods):
            self.environment.market_process(self.agent_list)
            self.environment.aspiration_update_process(self.agent_list)
            self.environment.technology_search_process(self.agent_list)
            self.environment.calculate_environment_result(self.agent_list)
            self.data_collector.collect(t)
        self.data_collector.save()
