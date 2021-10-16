# 这里要求用户把AgentParams excel表里的变量名字也写一遍吧，可以暂时赋值为0。虽然不是那么必要，但提升代码可读性。
# 此外，当然还得写agent的行为，这个文件肯定是必要的。
from Melodie import Agent


class DemoAgent(Agent):
    def setup(self):
        pass
