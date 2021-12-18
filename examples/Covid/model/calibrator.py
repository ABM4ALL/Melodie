
# 注册一张目标表，里面的数据结构不要求
# 根据表里的数据定义distance function，可以是好几个量的加权
# 这时候也注册一张scenario的表，但就只有一行了
# simulator跟trainer合作时候，scenarios和training_scenarios都可以有好多行（虽然后者可能只用一行），组合着train；
# 但是，simulator跟calibrator合作的时候，scenarios和calibrating_target就只有唯一的一对一组合关系。