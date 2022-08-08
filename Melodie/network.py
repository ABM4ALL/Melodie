import logging
from typing import Dict, Set, Union, List, Tuple, ClassVar, Callable, Type

from .boost.basics import Agent
from .boost.agent_list import AgentList

logger = logging.getLogger(__name__)


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
        pass

    def post_setup(self):
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
        self.edge_cls: ClassVar[Edge] = edge_cls if edge_cls is not None else Edge
        self.setup()

    def _setup(self):
        self.setup()

    def setup(self):
        pass

    def add_edge(self, source_id: NodeType, target_id: NodeType, edge: Edge):
        """
        Add an edge onto the network.
        :param source_id:
        :param target_id:
        :param edge
        :return:
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
        :return:
        """
        return self.edges[source_id][target_id]

    def remove_edge(self, source_id: NodeType, target_id: NodeType):
        """
        Remove an edge from the network

        :param source_id:
        :param target_id:
        :return:
        """
        self.edges[source_id].pop(target_id)
        if not self.directed:
            self.edges[target_id].pop(source_id)

    def _get_neighbor_positions(self, agent_id: int, category: int) -> List[Tuple[int, int]]:
        neighbor_ids = self.edges[(category, agent_id)]
        if neighbor_ids is None:
            return []
        else:
            return list(neighbor_ids.keys())

    def get_neighbors(self, agent: Agent):
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
        self._remove_agent(agent.category, agent.id)

    def add_agent(self, agent: Agent):
        self._add_agent(agent.category, agent.id)

    def create_edge(
            self,
            agent_1_id: int,
            category_1: int,
            agent_2_id: int,
            category_2: int,
            **edge_properties,
    ):
        edge = self.edge_cls(
            category_1, agent_1_id, category_2, agent_2_id, edge_properties
        )
        src_pos = (category_1, agent_1_id)
        dst_pos = (category_2, agent_2_id)
        assert src_pos in self.nodes
        assert dst_pos in self.nodes
        self.add_edge(src_pos, dst_pos, edge)

    def all_agents(self) -> Set[NodeType]:
        return self.nodes

    def get_node_edges(self, agent: Agent):
        targets = self.edges[(agent.category, agent.id)]
        edges: List[Edge] = []
        for target_node, edge in targets.items():
            edges.append(edge)
        return edges

    def setup_agent_connections(self,
                                agent_lists: List[AgentList],
                                network_type: str,
                                network_params: dict = None
                                ):
        import networkx as nx

        assert isinstance(agent_lists, list)
        node_id = 0
        node_id_to_node_type_map: Dict[int, NodeType] = {}
        for agent_list in agent_lists:
            category = agent_list[0].category
            assert isinstance(category, int)
            for agent in agent_list:
                self._add_agent(category, agent.id)
                node_id_to_node_type_map[node_id] = (category, agent.id)
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
