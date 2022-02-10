from Melodie import AgentList, Agent, Model, Scenario, Edge, AgentRelationshipNetwork
from tests.config import cfg


class RelationshipEdge(Edge):
    def setup(self):
        self.edge_a = 0
        self.edge_b = 12.0


class DemoAgentRelationshipNetwork(AgentRelationshipNetwork):
    def setup(self):
        self.edge_cls = RelationshipEdge


class DemoAgent(Agent):
    def setup(self):
        self.agent_a = 0
        self.agent_b = 0


class DemoModel(Model):
    def setup(self):
        self.agent_list = self.create_agent_container(DemoAgent, 10, )


def test_relationship_network():
    model = DemoModel(cfg, Scenario(0))
    model.setup()
    agent_list = AgentList(DemoAgent, 10, model)
    n = DemoAgentRelationshipNetwork()
    n.add_category('agents')
    for agent in agent_list:
        n.add_agent(agent.id, 'agents', agent.id)

    n.create_edge(agent_list[0].id, 'agents', agent_list[1].id, 'agents')
    n.create_edge(agent_list[0].id, 'agents', agent_list[2].id, 'agents')
    n.create_edge(agent_list[1].id, 'agents', agent_list[2].id, 'agents')
    n.create_edge(agent_list[3].id, 'agents', agent_list[4].id, 'agents')
    neighbor_ids = n.get_neighbors(agent_list[0].id, 'agents')
    assert len(neighbor_ids) == 2 and 1 in neighbor_ids and 2 in neighbor_ids

    n.add_agent(11, 'agents', 11)
    assert len(n.all_agents()) == 11
    assert 11 in n.all_agents()

    n.remove_agent(0, 'agents')

    assert len(n.get_neighbors(agent_list[1].id, 'agents')) == 1


def test_create_ba():
    def network_creator(agent_list):
        import networkx as nx
        return nx.barabasi_albert_graph(len(agent_list), 3)

    model = DemoModel(cfg, Scenario(0))
    model.setup()
    agent_list = AgentList(DemoAgent, 10, model)
    n = DemoAgentRelationshipNetwork()
    n.add_category('agents')
    n.from_agent_containers({'agents': agent_list}, 'barabasi_albert_graph', {'m': 3})
    assert len(n.all_agents()) == 10
    n.from_agent_containers({'agents': agent_list}, builder=network_creator)
    assert len(n.all_agents()) == 10

    agent_list2 = AgentList(DemoAgent, 10, model)

    n = DemoAgentRelationshipNetwork()
    n.from_agent_containers({'wolves': agent_list, "sheep": agent_list2}, 'barabasi_albert_graph', {'m': 3})
    raise NotImplementedError
    neighbors = n.get_neighbors(2, 'wolves')
    for node in neighbors:
        print(n.all_agent_on_node(node))
