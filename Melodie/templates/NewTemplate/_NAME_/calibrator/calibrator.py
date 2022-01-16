
from Melodie import Calibrator

class _ALIAS_CalibratorManager(Calibrator):
    pass

# calibrate分为两部分：
# agent_behavior, i.e. (offline) learning-based calibrator --> 设置要训练的agent的参数、取值范围，以及训练算法(social learning / individual learning)
# env_params --> 设置要calibrate环境参数以及它们的取值范围，然后是sample, measure, and search api

# calibration和simulation，都是凑好一组scenario package输入到模型里跑。区别在于：
# simulation的scenario是顺着表跑就好了，calibration是由feedback (distance)驱动搜索，迭代出的下一组参数。
