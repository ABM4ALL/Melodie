from typing import TYPE_CHECKING
from Melodie import Edge, Network

if TYPE_CHECKING:
    from Melodie import AgentList
    from .agent import CovidAgent
    from .scenario import CovidScenario


class CovidEdge(Edge):

    # 如果edge的属性值是基于被连接的两个agent的attribute算出来的，那就总可以用check_neighbors做到。
    # 所以，似乎除了提速，没必要给edge属性。
    # 例如：来自同age_group的影响权重为2，不同的为1 --> social influence = sum(w * value)/sum(w * 1)

    # 那么，"让edge有自己的attribute"到底是不是伪需求？
    # 不是，有如下情形：
    # 第一，如果environment可以改edge的属性，比如强弱，那就必须让edge有自己的attribute了。

    pass


class CovidNetwork(Network):

    def setup(self):
        pass
