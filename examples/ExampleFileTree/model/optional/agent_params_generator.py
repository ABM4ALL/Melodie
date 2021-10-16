


# 还是原来的table_generator的作用，只不过明确地把功能限定为设置初始化agent的参数了
# 避免用agent_manager这个名字，还是为了避免混淆，让它留在后面吧。


# agent params的初始化
# 1. 基于AgentParams的excel表初始化：不考虑不同scenario里AgentParams不同（为了控制变量也不应该变），之前想多了 --> 这种情况下就不需要AgentParamsGenerator
# 2. AgentParamsGenerator（原来的table_generator） --> 返回一张dataframe表，存到数据库里，并给agent_manager完成最后的agent_list初始化
# 2.1 最简单的情况，是直接用类似于现在的add方法，基于scenario params生成agent params的dataframe。
# 2.2 复杂一点，一是可能用到static tables，二是参数之间可能有依赖关系。这种情况也可以让用户自己写吧，总之就是返回一张dataframe表，存到数据库里，
#     并交给agent_manager，完成最后的agent_list初始化。这样整个下来的结果，就跟从数据库里读AgentParams是一样的，用一个dataframe设置所有agent的参数，
#     column_name就是agent的attribute名字。这张表也需要存，因为最后分析结果可能会用到AgentParams。
# 2.3 对于模拟过程中用到的参数/AgentVar，比如每期的收益，虽然不用初始化，但也放到这里一起，初始化为0就好了。

class AgentParamsGenerator:
    pass


