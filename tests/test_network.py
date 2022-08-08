from Melodie import AgentList, Agent, Model, Scenario, Edge, Network
from tests.config import cfg


class RelationshipEdge(Edge):
    def setup(self):
        self.edge_a = 0
        self.edge_b = 12.0


class DemoNetwork(Network):
    def setup(self):
        self.edge_cls = RelationshipEdge


class DemoAgent(Agent):
    # def set_category(self):

    def setup(self):
        self.agent_a = 0
        self.agent_b = 0
        self.category = 0


class Wolf(Agent):
    # def set_category(self):

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
    n.add_category("agents")
    for agent in agent_list:
        n.add_agent(agent.id, "agents", agent.id)

    n.create_edge(agent_list[0].id, "agents", agent_list[1].id, "agents")
    n.create_edge(agent_list[0].id, "agents", agent_list[2].id, "agents")
    n.create_edge(agent_list[1].id, "agents", agent_list[2].id, "agents")
    n.create_edge(agent_list[3].id, "agents", agent_list[4].id, "agents")
    neighbor_ids = n.get_neighbor_positions(agent_list[0].id, "agents")
    assert (
            len(neighbor_ids) == 2
            and ("agents", 1) in neighbor_ids
            and ("agents", 2) in neighbor_ids
    )

    n.add_agent(11, "agents", 11)
    assert len(n.all_agents()) == 11
    assert 11 in n.all_agents()

    n.remove_agent(0, "agents")

    assert len(n.get_neighbor_positions(agent_list[1].id, "agents")) == 1


def test_relationship_directed():
    model = DemoModel(cfg, Scenario(0))
    model.setup()
    agent_list = AgentList(DemoAgent, model)
    agent_list.setup_agents(10)
    n = DemoNetwork(directed=True)
    n.add_category("agents")
    for agent in agent_list:
        n.add_agent(agent.id, "agents", agent.id)

    n.create_edge(agent_list[0].id, "agents", agent_list[1].id, "agents")
    n.create_edge(agent_list[0].id, "agents", agent_list[2].id, "agents")
    n.create_edge(agent_list[1].id, "agents", agent_list[2].id, "agents")
    n.create_edge(agent_list[3].id, "agents", agent_list[4].id, "agents")
    neighbor_ids = n.get_neighbor_positions(agent_list[0].id, "agents")
    assert (
            len(neighbor_ids) == 2
            and ("agents", 1) in neighbor_ids
            and ("agents", 2) in neighbor_ids
    )

    n.add_agent(11, "agents", 11)
    assert len(n.all_agents()) == 11
    assert 11 in n.all_agents()

    n.remove_agent(0, "agents")
    print(n._adj)
    assert len(n.get_neighbor_positions(agent_list[1].id, "agents")) == 1


def test_create_ba():
    def network_creator(agent_list):
        import networkx as nx

        return nx.barabasi_albert_graph(len(agent_list), 3)

    model = DemoModel(cfg, Scenario(0))
    model.setup()
    agent_list = AgentList(DemoAgent, model)
    agent_list.setup_agents(10)
    n = DemoNetwork.from_agent_lists(
        [agent_list], "barabasi_albert_graph", {"m": 3}
    )
    assert len(n.all_agents()) == 10
    n = DemoNetwork.from_agent_lists(
        [agent_list], builder=network_creator
    )
    assert len(n.all_agents()) == 10

    agent_list2 = AgentList(Wolf, model)
    agent_list2.setup_agents(10)
    n = DemoNetwork()
    n.setup_agent_connections(
        [agent_list, agent_list2],
        "watts_strogatz_graph",
        {"k": 3, "p": 0.2},
    )
    for i in range(10):
        neighbors = n.get_neighbor_positions(i, 1)
        print(neighbors)
    # for node in neighbors:
    #     print(n.all_agent_on_node(node))
