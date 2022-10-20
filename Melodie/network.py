import logging
from typing import Dict, Set, Union, List, Tuple, Type

from .boost.basics import Agent
from .boost.agent_list import AgentList

logger = logging.getLogger(__name__)


class NetworkAgent(Agent):
    id: int
    category: int
    network: "Network"

    def _set_network(self, network: "Network"):
        self.network = network

    def set_category(self):
        """
        Set the category of network agent.

        :return:
        """
        raise NotImplementedError(
            "Method `set_category` should be implemented for custom NetworkAgent."
        )


class Edge:
    def __init__(
        self,
        category_1: int,
        agent_1_id: int,
        category_2: int,
        agent_2_id: int,
        edge_properties: Dict[str, Union[int, str, float, bool]],
    ):
        self.category_1 = category_1
        self.agent_1_id = agent_1_id
        self.category_2 = category_2
        self.agent_2_id = agent_2_id
        self.properties: Dict[str, Union[int, str, float, bool]] = edge_properties
        self.setup()
        self.post_setup()

    def setup(self):
        """
        Setup method. Be sure to inherit it for custom Edge.

        :return: None
        """
        pass

    def post_setup(self):
        """
        This method is executed after `setup()`

        :return: None
        """
        for prop_name, prop_value in self.properties.items():
            setattr(self, prop_name, prop_value)

    def __repr__(self):
        return f"<{self.__class__.__name__} {(self.category_1, self.agent_1_id)} --> {(self.category_2, self.agent_2_id)}>"


NodeType = Tuple[int, int]


class Network:
    def __init__(self, edge_cls: Type[Edge] = None, directed=False):
        self.simple = True
        self.directed = directed
        self.nodes: Set[NodeType] = set()
        self.edges: Dict[NodeType, Dict[NodeType, Edge]] = {}
        self.edge_cls: Type[Edge] = edge_cls if edge_cls is not None else Edge
        self.setup()

    def _setup(self):
        self.setup()

    def setup(self):
        """
        Setup function of network. Be sure to inherit this method for custom implementation.

        :return: None
        """
        pass

    def add_edge(self, source_id: NodeType, target_id: NodeType, edge: Edge):
        """
        Add an edge onto the network.

        :param source_id:
        :param target_id:
        :param edge
        :return: None
        """
        if source_id not in self.edges:
            self.edges[source_id] = {}
        self.edges[source_id][target_id] = edge
        if not self.directed:
            if target_id not in self.edges:
                self.edges[target_id] = {}
            self.edges[target_id][source_id] = edge

    def get_edge(self, source_id: NodeType, target_id: NodeType):
        """
        Get an edge from the network

        :param source_id:
        :param target_id:
        :return: An `Edge` object
        """
        return self.edges[source_id][target_id]

    def remove_edge(self, source_id: NodeType, target_id: NodeType):
        """
        Remove an edge from the network

        :param source_id:
        :param target_id:
        :return: None
        """
        self.edges[source_id].pop(target_id)
        if not self.directed:
            self.edges[target_id].pop(source_id)

    def _get_neighbor_positions(
        self, agent_id: int, category: int
    ) -> List[Tuple[int, int]]:
        neighbor_ids = self.edges[(category, agent_id)]
        if neighbor_ids is None:
            return []
        else:
            return list(neighbor_ids.keys())

    def get_neighbors(self, agent: Agent):
        """
        Get surrounding neighbors of agent.

        :param agent:
        :return:
        """
        assert hasattr(agent, "category")
        return self._get_neighbor_positions(agent.id, agent.category)

    def _add_agent(self, category: int, agent_id: int):
        """

        :param agent_id:
        :param category:
        :param agent_id:
        :return:
        """
        agent_tuple: NodeType = (category, agent_id)
        self.nodes.add(agent_tuple)

    def _remove_agent(self, category: int, agent_id: int):
        """

        :param agent_id:
        :param category:
        :return:
        """
        agent_tuple = (category, agent_id)
        self.nodes.remove(agent_tuple)
        target_edges = self.edges.pop(agent_tuple)
        if not self.directed:
            for target_node, edge in target_edges.items():
                self.edges[target_node].pop(agent_tuple)

    def remove_agent(self, agent: Agent):
        """
        Remove agent from network

        :param agent: Agent
        :return: None
        """
        assert hasattr(agent, "category")
        self._remove_agent(agent.category, agent.id)

    def add_agent(self, agent: Agent):
        """
        Add an agent onto the network.

        :param agent:
        :return:
        """
        assert isinstance(agent, NetworkAgent)
        agent.set_category()
        agent._set_network(self)
        self._add_agent(agent.category, agent.id)

    def create_edge(
        self,
        agent_1_id: int,
        category_1: int,
        agent_2_id: int,
        category_2: int,
        **edge_properties,
    ):
        """
        Create a new edge from one agent to another agent.

        :param agent_1_id:
        :param category_1:
        :param agent_2_id:
        :param category_2:
        :param edge_properties:
        :return:
        """
        edge = self.edge_cls(
            category_1, agent_1_id, category_2, agent_2_id, edge_properties
        )
        src_pos = (category_1, agent_1_id)
        dst_pos = (category_2, agent_2_id)
        assert src_pos in self.nodes
        assert dst_pos in self.nodes
        self.add_edge(src_pos, dst_pos, edge)

    def all_agents(self) -> Set[NodeType]:
        """
        Get all agents on the network.

        :return: A list of (`Agent category`, `Agent id`)
        """
        return self.nodes

    def get_node_edges(self, agent: Agent):
        """
        Get the edges from one node.

        :param agent:
        :return:
        """
        assert isinstance(agent, NetworkAgent)
        targets = self.edges[(agent.category, agent.id)]
        edges: List[Edge] = []
        for target_node, edge in targets.items():
            edges.append(edge)
        return edges

    def setup_agent_connections(
        self,
        agent_lists: List[AgentList],
        network_type: str,
        network_params: dict = None,
    ):
        """
        Set up the connection between agents.
        The name and parameters come from NetworkX package. For example, The documentation for BA scale-free network
        is here: https://networkx.org/documentation/stable/reference/generated/networkx.generators.random_graphs.barabasi_albert_graph.html.
        To create it, network_type is `barabasi_albert_graph`, and parameters should be a dict {"n": 100, "m": 3}.

        :param agent_lists:
        :param network_type: str, describing the type of network, which should be the corresponding to networkx.
        :param network_params: A dictionary for parameter values.
        :return: None
        """
        import networkx as nx

        assert isinstance(agent_lists, list)
        node_id = 0
        node_id_to_node_type_map: Dict[int, NodeType] = {}
        for agent_list in agent_lists:
            # category = agent_list[0].category
            # assert isinstance(category, int)
            for agent in agent_list:
                self.add_agent(agent)
                agent._set_network(self)
                node_id_to_node_type_map[node_id] = (agent.category, agent.id)
                node_id += 1

        g = getattr(nx, network_type)(
            len(self.nodes),
            **network_params,
        )

        for edge in g.edges:
            agent_src = node_id_to_node_type_map[edge[0]]
            agent_dest = node_id_to_node_type_map[edge[1]]
            edge_obj = self.edge_cls(
                agent_src[0], agent_src[1], agent_dest[0], agent_dest[1], {}
            )
            self.add_edge(agent_src, agent_dest, edge_obj)
        self._nx_edges = list(g.edges)
