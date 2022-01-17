
# 1. 注册一张目标表，里面的数据结构不要求
#  - 单个数
#  - 一条或甚至多条序列

# 2. 根据表里的数据定义distance function
#  - calibrator里面的@abstractmethod (loss, similar to fitness function in trainer, but it is opposite)
#  - Conceptually, "distance" is opposite to "fitness", so in the GA behind, we need to convert the DanDiaoXing.



# 这时候也注册一张scenario的表，但就只有一行了，标记待calibrate的参数，以及这些参数的范围
# simulator跟trainer合作时候，scenarios和training_scenarios都可以有好多行（虽然后者可能只用一行），组合着train；
# 但是，simulator跟calibrator合作的时候，scenarios和calibrating_target就只有唯一的一对一组合关系。





# register
# value ranges of param_1, param_2, param_3



# Calibrator includes following functions

# @abstractmethod
def setup(self):
    self.add_property('scenario', 'param_1')
    self.add_property('scenario', 'param_2')
    self.add_property('scenario', 'param_3')

# @abstractmethod
def distance(self, agent: AspirationAgent):
    return agent.account



def convert_distance_to_fitness():
    pass

def set_algorithm():
    pass
