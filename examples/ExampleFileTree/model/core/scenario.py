# 感觉这个文件可能不是很必要。但如果这里要求用户把Scenario excel表里的列名字也写一遍，可以暂时赋值为0，增强代码可读性。
# 在agent或env里通过scenario访问情景参数、static tables里的数据。

from Melodie import Scenario


class DemoScenario(Scenario):
    def setup(self):
        pass
