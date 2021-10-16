
import pandas as pd
from typing import Optional

class NewScenario:

    # 一个完整的scenario是初始化并运行模型需要的所有外生参数的集合，包括两部分：
    # 1. scenario_series = scenario_id +
    #    1.1 env_params: number_of_run, number_of_period, number_of_agent, rich_win_prob等
    #    1.2 [optional] agent_params: parameters that are used to generate agent_params_dataframe
    # 2. [optional] static_tables, including:
    #    2.1 agent_params_dataframe --> assert len(AgentParams) == number_of_agent
    #    2.2 other static_table
    # 以上所有一开始都存在excel_source文件夹里，之后导入sqlite数据库。

    def __init__(self,
                 attribute_series: dict,
                 agent_params_dataframe: pd.DataFrame,
                 static_tables: Optional[dict]):
        pass

