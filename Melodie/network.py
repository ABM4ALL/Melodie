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


NodeType = Tuple[int, int]


class Network:
    def __init__(self, edge_cls: Type[Edge] = None, directed=False):
        self.simple = True
        self.directed = directed
        self._nodes: Set[NodeType] = set()
        self._edges: Dict[NodeType, Dict[NodeType, Edge]] = {}
        # self._adj: Dict[int, Dict[int, Edge]] = {}
        # self._agent_ids: Dict[
        #     int, Dict[int, Set[int]]
        # ] = {}  # {category_id: {0 : set(1, 2, 3)}}
        # self._agent_pos: Dict[int, Dict[int, int]] = {}  # {'wolves': {0: 1}}
        self.edge_cls: ClassVar[Edge] = edge_cls if edge_cls is not None else Edge
        self.setup()
        self._nx_edges = None

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
        if source_id not in self._edges:
            self._edges[source_id] = {}
        self._edges[source_id][target_id] = edge
        if not self.directed:
            if target_id not in self._edges:
                self._edges[target_id] = {}
            self._edges[target_id][source_id] = edge

    def get_edge_directed(self, source_id: NodeType, target_id: NodeType):
        """
        Get an edge from the network
        :param source_id:
        :param target_id:
        :return:
        """
        return self._edges[source_id][target_id]

    def get_edge(self, source_id: NodeType, target_id: NodeType):
        try:
            self.get_edge_directed(source_id, target_id)
        except KeyError:
            self.get_edge_directed(target_id, source_id)

    def remove_edge(self, source_id: NodeType, target_id: NodeType):
        """
        Remove an edge from the network

        :param source_id:
        :param target_id:
        :return:
        """
        self._edges[source_id].pop(target_id)
        if not self.directed:
            self._edges[target_id].pop(source_id)

    def get_neighbor_positions(self, agent_id: int, category: int) -> List[Tuple[int, int]]:
        neighbor_ids = self._edges[(category, agent_id)]
        if neighbor_ids is None:
            return []
        else:
            return list(neighbor_ids.keys())

    def get_neighbors(self, agent: Agent):
        assert hasattr(agent, "category")
        return self.get_neighbor_positions(agent.id, agent.category)

    def _add_agent(self, category: int, agent_id: int):
        """

        :param agent_id:
        :param category:
        :param agent_id:
        :return:
        """
        agent_tuple: NodeType = (category, agent_id)
        self._nodes.add(agent_tuple)

    def _remove_agent(self, category: int, agent_id: int):
        """

        :param agent_id:
        :param category:
        :return:
        """
        agent_tuple = (category, agent_id)
        self._nodes.remove(agent_tuple)
        target_edges = self._edges.pop(agent_tuple)
        if not self.directed:
            for target_node, edge in target_edges.items():
                self._edges[target_node].pop(agent_tuple)

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
        self.add_edge(src_pos, dst_pos, edge)

    def all_agents(self) -> Set[NodeType]:
        return self._nodes

    # def all_agent_on_node(self, node_id) -> List[Tuple[int, int]]:
    #     l = []
    #     for category_id, ids_in_category in self._agent_ids.items():
    #         agent_ids = ids_in_category.get(node_id)
    #         if agent_ids is not None:
    #             l.extend([(category_id, agent_id) for agent_id in agent_ids])
    #     return l

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
            len(self._nodes),
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

    @classmethod
    def from_agent_lists(
            cls,
            agent_lists: "List[AgentList]",
            network_name: str = "",
            network_params: dict = "",
            builder: Callable = None,
    ):
        """
        :param agent_lists: a list of AgentList
        :param network_name: The name of network.
        :param network_params: The parameters of network
        :param builder: The network builder function.
            - One argument, a list of int representing nodes;
            - One return as nx.Graph

        It is suggested to use builder argument for more freedom of customization.

        :return:
        """
        self = cls()
        import networkx as nx

        assert isinstance(agent_lists, list)
        node_id = 0
        for agent_list in agent_lists:
            category = agent_list[0].category
            assert isinstance(category, int)
            for agent in agent_list:
                self._add_agent(agent.id, category)
                node_id += 1

        if builder is not None:
            g = builder(self._nodes)
        else:
            if network_name == "barabasi_albert_graph":
                g = nx.__getattribute__(network_name)(
                    len(self._nodes),
                    **network_params,
                )
            elif network_name == "watts_strogatz_graph":
                g = nx.__getattribute__(network_name)(
                    len(self._nodes),
                    **network_params,
                )
            else:
                raise NotImplementedError(
                    f"Network name {network_name} is not implemented!"
                )

        for edge in g.edges:
            agent_src = list(self.all_agent_on_node(edge[0]))[0]
            agent_dest = list(self.all_agent_on_node(edge[1]))[0]
            edge_obj = self.edge_cls(
                agent_src[0], agent_src[1], agent_dest[0], agent_dest[1], {}
            )
            self.add_edge(edge[0], edge[1], edge_obj)
        return self
