from Melodie import AgentList, Agent, Model, Scenario, Edge, Network
from Melodie.network import NetworkAgent
from tests.config import cfg


class RelationshipEdge(Edge):
    def setup(self):
        self.edge_a = 0
        self.edge_b = 12.0


class DemoNetwork(Network):
    def setup(self):
        self.edge_cls = RelationshipEdge


class DemoAgent(NetworkAgent):
    def set_category(self):
        return 0

    def setup(self):
        self.agent_a = 0
        self.agent_b = 0
        self.category = 0


class Wolf(NetworkAgent):
    def set_category(self):
        return 1

    def setup(self):
        self.agent_a = 0
        self.agent_b = 0
        self.category = 1


class DemoModel(Model):
    def setup(self):
        self.agent_list = self.create_agent_container(
            DemoAgent,
            10,
        )


def test_relationship_network():
    model = DemoModel(cfg, Scenario(0))
    model.setup()
    agent_list = AgentList(DemoAgent, model)
    agent_list.setup_agents(10)
    n = DemoNetwork()
    # n.add_category("agents")
    for agent in agent_list:
        n._add_agent("agents", agent.id)

    n.create_edge(agent_list[0].id, "agents", agent_list[1].id, "agents")
    n.create_edge(agent_list[0].id, "agents", agent_list[2].id, "agents")
    n.create_edge(agent_list[1].id, "agents", agent_list[2].id, "agents")
    n.create_edge(agent_list[3].id, "agents", agent_list[4].id, "agents")
    neighbor_ids = n._get_neighbor_positions(agent_list[0].id, "agents")
    assert (
            len(neighbor_ids) == 2
            and ("agents", 1) in neighbor_ids
            and ("agents", 2) in neighbor_ids
    )

    n._add_agent("agents", 11)
    assert len(n.all_agents()) == 11
    assert ("agents", 11) in n.all_agents()

    n._remove_agent("agents", 0)

    assert len(n._get_neighbor_positions(agent_list[1].id, "agents")) == 1


def test_relationship_directed():
    model = DemoModel(cfg, Scenario(0))
    model.setup()
    agent_list = AgentList(DemoAgent, model)
    agent_list.setup_agents(10)
    n = DemoNetwork(directed=True)
    for agent in agent_list:
        n._add_agent(
            "agents",
            agent.id,
        )

    n.create_edge(agent_list[0].id, "agents", agent_list[1].id, "agents")
    n.create_edge(agent_list[0].id, "agents", agent_list[2].id, "agents")
    n.create_edge(agent_list[1].id, "agents", agent_list[2].id, "agents")
    n.create_edge(agent_list[3].id, "agents", agent_list[4].id, "agents")
    neighbor_ids = n._get_neighbor_positions(agent_list[0].id, "agents")
    assert (
            len(neighbor_ids) == 2
            and ("agents", 1) in neighbor_ids
            and ("agents", 2) in neighbor_ids
    )

    n._add_agent(
        "agents",
        11,
    )
    assert len(n.all_agents()) == 11
    assert ("agents", 11) in n.all_agents()

    n._remove_agent(
        "agents",
        0,
    )
    assert len(n._get_neighbor_positions(agent_list[1].id, "agents")) == 1


def test_create_ba():
    def network_creator(agent_list):
        import networkx as nx

        return nx.barabasi_albert_graph(len(agent_list), 3)

    model = DemoModel(cfg, Scenario(0))
    model.setup()
    agent_list = AgentList(DemoAgent, model)
    agent_list.setup_agents(10)

    agent_list2 = AgentList(Wolf, model)
    agent_list2.setup_agents(10)
    n = DemoNetwork()
    n.setup_agent_connections(
        [agent_list, agent_list2],
        "watts_strogatz_graph",
        {"k": 3, "p": 0.2},
    )
    for i in range(10):
        neighbors = n._get_neighbor_positions(i, 1)
        print(neighbors)
        print("edges", n.get_node_edges(agent_list2.get_agent(i)))
    # for node in neighbors:
    #     print(n.all_agent_on_node(node))
