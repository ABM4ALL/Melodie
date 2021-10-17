
from typing import List, Optional
import pandas as pd

from Melodie import NewScenario, SimulatorManager




# 似乎无论是simulator还是calibrator，都只写相应的manager就可以了，scenario不用出现在任何文件里？
class _ALIAS_Scenario(NewScenario):

    # 一个完整的scenario是初始化并运行模型需要的所有外生参数的集合，包括两部分：
    # 1. scenario_series = scenario_id +
    #    1.1 env_params: number_of_run, number_of_period, number_of_agent, rich_win_prob等
    #    1.2 [optional] agent_params: parameters that are used to generate agent_params_dataframe
    # 2. [optional] static_tables, including:
    #    2.1 agent_params_dataframe --> assert len(AgentParams) == number_of_agent
    #    2.2 other static_table
    # 以上所有一开始都存在excel_source文件夹里，之后导入sqlite数据库。

    pass





class DemoSimulatorManager(SimulatorManager):

    def register_static_tables(self):
        # 这个函数必须写：注册每一张excel_source文件夹里的表，包括：变量名、表名、列名、列数据类型。
        # 1. 注册Scenarios.xlsx
        # 2. 注册其他的static_table
        #  - assert以上写对了 --> 虽然麻烦，但可以帮助用户少犯错。
        # 把这些表导入sqlite数据库。
        pass

    def generate_agent_params_dataframe(self):
        # 这个函数必须写，分两种情况
        # (A) 最简单的，直接让agent_params_dataframe等于某张static_table。
        # (B) 自己写函数，基于1.2和2.1生成agent_params_dataframe
        #     (B1) 最简单的情况，是直接用类似于现在的add方法，基于1.2生成agent_params_dataframe。
        #     (B2) 复杂一点，比如参数之间有依赖关系、用到1.2和2.1，让用户自己写函数生成agent_params_dataframe。
        # 补充：有些参数无关启动模型，属于中间结果（比如每期的收益），此处初始化为0。
        pass

    def generate_scenarios(self) -> List[DemoScenario]:
        # 对每个Scenario的实例，初始化三部分：
        # 1. attributes --> Scenarios.xlsx里的一行
        # 2. agent_params_table --> 用于model.setup_agent_list
        # 3. Scenarios以外的static_table
        # 之后，在agent和env里面，可以直接用scenario.name访问这些attributes和表。
        pass

