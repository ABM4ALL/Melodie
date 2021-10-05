
class Calibrator:
    pass


# Calibrator是用simulation-based calibration的方法校准【选出的一部分】enviornment parameters
# 先对所有参数做敏感性分析，找出重要的calibrate，
# 给要calibrate的参数设定空间，然后sampling，再搜索。
# 搜索的时候涉及两部分：
# 第一，定义simulated output和real data之间的距离，这个有不同度量方法；
# 第二，返回某个参数组合的“距离”后，怎么迭代搜索到下一组参数组合。