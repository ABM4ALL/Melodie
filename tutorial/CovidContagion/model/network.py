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

    # 需要让network能够访问scenario

    def generate_network(self, agents: 'AgentList[CovidAgent]', scenario: 'CovidScenario'):
        if scenario.network_type == 0:
            k = scenario.network_param_k
            p = scenario.network_param_p
            network = self.generate_small_world_network(agents, k, p)
        elif scenario.network_type == 1:
            m = scenario.network_param_m
            network = self.generate_scale_free_network(agents, m)
        else:
            network = None
            print(f"The id_network_type = {scenario.network_type} is not implemented.")
        return network

    def generate_small_world_network(self, agents: 'AgentList[CovidAgent]', k: int, p: float):
        network = self.from_agent_containers(
            {'agents': agents},
            'watts_strogatz_graph',
            {'k': k, 'p': p}
        )
        return network

    def generate_scale_free_network(self, agents: 'AgentList[CovidAgent]', m: int):
        network = self.from_agent_containers(
            {'agents': agents},
            'barabasi_albert_graph',
            {'m': m}
        )
        return network


