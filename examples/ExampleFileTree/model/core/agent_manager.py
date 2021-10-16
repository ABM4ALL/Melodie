# 现在这个类好像主要就是用来初始化agent的了 --> 替代了原来的table_generator的作用。
# 如果同时有agent和agent_manager，感觉有点儿重复。


# agent_list初始化的时候
# 1. 基于AgentParams表初始化：不考虑不同scenario里AgentParams不同的情况（为了控制变量也不应该变）
# 2. table_generator --> 缩小范围到agent_params_generator，在agent_manager下使用
# 2.1 最简单的情况，是直接用简单函数，基于scenario params生成agent params的dataframe。
# 2.2 复杂一点，一是可能用到static tables，二是参数之间可能有依赖关系。这种情况也可以让用户自己写吧。不管是用add还是自己写，
#     最后都是生成一张dataframe表，存到数据库里，同时初始化所有agent的attributes。这样就跟从数据库里读AgentParams是一样的，
#     用一个dataframe设置所有agent的参数，column_name就是agent的attribute名字。这张表也需要存，因为最后分析结果可能会用到AgentParams。
# 2.3 对于模拟过程中用到的参数/AgentVar，比如每期的收益，虽然不用初始化，但也放到这里一起，初始化为0就好了。
from Melodie import AgentManager


class DemoAgentManager(AgentManager):
    def setup(self):
        pass
