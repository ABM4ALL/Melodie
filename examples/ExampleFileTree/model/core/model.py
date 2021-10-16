from Melodie import Model


# class Model:
#     def __init__(self,
#                  config: 'Config',
#                  agent_class: ClassVar[Agent],
#                  environment_class: ClassVar[Environment],
#                  data_collector_class: ClassVar[DataCollector] = None, --> 可以改成必选项
#                  table_generator_class: ClassVar[TableGenerator] = None, --> 去掉了，合并到agent_manager下面去了
#                  scenario: Scenario = None,  -->
#                  run_id_in_scenario: int = 0
#                  ):
#         pass


class DemoModel(Model):
    def setup(self):
        pass

    def run(self):
        simulation_periods = self.scenario.periods
        agent_manager = self.agent_manager
        dc = self.data_collector

        for t in range(0, simulation_periods):
            print("ID_Scenario = " + str(self.scenario.id) + ", period = " + str(t))

            self.environment.go_money_produce(agent_manager)
            self.environment.go_money_transfer(agent_manager)
            self.environment.calc_wealth_and_gini(agent_manager)
            dc.collect(t)
        dc.save()
# 这里为啥没看到Melodie.model里的那个step函数？
