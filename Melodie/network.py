from typing import Dict, Set, Union, List, Tuple, ClassVar, Callable

import logging

from .boost.agent_list import AgentList

logger = logging.getLogger(__name__)


class Edge:

    def __init__(self, category_1: str, agent_1_id: int, category_2: str, agent_2_id: int,
                 edge_properties: Dict[str, Union[int, str, float, bool]]):
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


class OldNetwork:
    def __init__(self):
        self.simple = True
        # self._nodes: Set[int] = set()
        self._adj: Dict[int, Union[Set[int], List[int]]] = {}
        self._agent_ids: Dict[
            str, Dict[int, Set[int]]] = {}  # {'wolves': {0 : set(1, 2, 3)}}: there are 1,2,3 three wolves on #0 node
        self._agent_pos: Dict[str, Dict[int, int]] = {}  # {'wolves': {0: 1}}: there are wolve #0 on #1 node

    def add_category(self, category_name: str):
        """
        Add category
        :param category_name:
        :return:
        """
        self._agent_ids[category_name] = {}
        self._agent_pos[category_name] = {}

    def add_edge(self, source_id: int, target_id: int):
        """
        Add an edge onto the network.
        :param source_id: 
        :param target_id: 
        :return: 
        """
        # if source_id not in self._nodes:
        #     self.add_node(source_id)
        # if target_id not in self._nodes:
        #     self.add_node(target_id)

        if source_id not in self._adj.keys():
            self._adj[source_id] = set()
        if target_id not in self._adj.keys():
            self._adj[target_id] = set()
        self._adj[source_id].add(target_id)
        self._adj[target_id].add(source_id)

    def remove_edge(self, source_id: int, target_id: int):
        """
        Remove an edge from the network
        :param source_id:
        :param target_id:
        :return:
        """
        self._adj[source_id].remove(target_id)
        self._adj[target_id].remove(source_id)

    def get_neighbors(self, node: int) -> List[int]:

        neighbor_ids = self._adj.get(node)
        if neighbor_ids is None:
            return []
        else:
            return neighbor_ids

    def add_edges(self, edges: List[Tuple[int, int]]):
        for edge in edges:
            self.add_edge(edge[0], edge[1])

    def add_agent(self, agent_id: int, category: str, node_id: int):
        """

        :param agent_id:
        :param category:
        :param node_id:
        :return:
        """
        assert agent_id not in self._agent_ids
        if node_id not in self._agent_ids[category]:
            self._agent_ids[category][node_id] = set()
        self._agent_ids[category][node_id].add(agent_id)
        self._agent_pos[category][agent_id] = node_id

    def remove_agent(self, agent_id: int, category: str):
        """

        :param agent_id:
        :param category:
        :return:
        """
        assert category in self._agent_ids
        node_id: int = self._agent_pos[category].pop(agent_id)
        self._agent_ids[category][node_id].remove(agent_id)

    def move_agent(self, agent_id: int, category: str, target_node_id: int):
        """

        :param agent_id:
        :param category:
        :param target_node_id:
        :return:
        """
        self.remove_agent(agent_id, category)
        self.add_agent(agent_id, category, target_node_id)

    def get_agents(self, category: str, node_id: int):
        """

        :param category:
        :param node_id:
        :return:
        """
        if node_id not in self._agent_ids[category].keys():
            return set()
        else:
            return self._agent_ids[category][node_id]

    def agent_pos(self, agent_id: int, category: str):
        return self._agent_pos[category][agent_id]

    def create_edge(self,
                    category_1: str, agent_1_id: int,
                    category_2: str, agent_2_id: int,
                    **edge_properties):
        edge = Edge(category_1, agent_1_id,
                    category_2, agent_2_id,
                    edge_properties)
        self.add_edge(edge)


class Network:

    def __init__(self, directed=False):
        self.simple = True
        self.directed = directed
        self._nodes: Set[int] = set()
        self._adj: Dict[int, Dict[int, Edge]] = {}
        self._agent_ids: Dict[str, Dict[int, Set[int]]] = {}  # {'wolves': {0 : set(1, 2, 3)}}
        self._agent_pos: Dict[str, Dict[int, int]] = {}  # {'wolves': {0: 1}}
        self.edge_cls: ClassVar[Edge] = Edge
        self.setup()

    def setup(self):
        pass

    def add_category(self, category_name: str):
        """
        Add category
        :param category_name:
        :return:
        """
        self._agent_ids[category_name] = {}
        self._agent_pos[category_name] = {}

    def add_edge(self, source_id: int, target_id: int, edge: Edge):
        """
        Add an edge onto the network.
        :param source_id:
        :param target_id:
        :param edge
        :return:
        """

        if source_id not in self._adj.keys():
            self._adj[source_id] = {}
        if target_id not in self._adj.keys():
            self._adj[target_id] = {}
        self._adj[source_id][target_id] = edge
        if not self.directed:
            self._adj[target_id][source_id] = edge

    def remove_edge(self, source_id: int, target_id: int):
        """
        Remove an edge from the network
        :param source_id:
        :param target_id:
        :return:
        """
        self._adj[source_id].pop(target_id)
        if not self.directed:
            self._adj[target_id].pop(source_id)

    def get_neighbors(self, agent_id: int, category: str) -> List[int]:
        node_id = self.agent_pos(agent_id, category)
        neighbor_ids = self._adj.get(node_id)
        if neighbor_ids is None:
            return []
        else:
            neighbor_agent_ids_list = []
            for neighbor_id in neighbor_ids.keys():
                agents = self.all_agent_on_node(neighbor_id)
                neighbor_agent_ids_list.extend(agents)
            return neighbor_agent_ids_list

    def add_edges(self, edges: List[Tuple[int, int]]):
        """
        Add multiple edges onto the network.
        :param edges:
        :return:
        """
        for edge in edges:
            self.add_edge(edge[0], edge[1])

    def add_agent(self, agent_id: int, category: str, node_id: int):
        """

        :param agent_id:
        :param category:
        :param node_id:
        :return:
        """
        assert agent_id not in self._agent_ids
        if node_id not in self._agent_ids[category]:
            self._agent_ids[category][node_id] = set()
        if node_id not in self._nodes:
            self._nodes.add(node_id)
        self._agent_ids[category][node_id].add(agent_id)
        self._agent_pos[category][agent_id] = node_id

    def remove_agent(self, agent_id: int, category: str):
        """

        :param agent_id:
        :param category:
        :return:
        """
        assert category in self._agent_ids
        node_id: int = self._agent_pos[category].pop(agent_id)
        self._agent_ids[category][node_id].remove(agent_id)
        self._nodes.remove(node_id)
        target_edges = self._adj.pop(agent_id)
        if not self.directed:
            for target_node, edge in target_edges.items():
                self._adj[target_node].pop(node_id)

    def move_agent(self, agent_id: int, category: str, target_node_id: int):
        """

        :param agent_id:
        :param category:
        :param target_node_id:
        :return:
        """
        self.remove_agent(agent_id, category)
        self.add_agent(agent_id, category, target_node_id)

    def get_agents(self, category: str, node_id: int):
        """

        :param category:
        :param node_id:
        :return:
        """
        if node_id not in self._agent_ids[category].keys():
            return set()
        else:
            return self._agent_ids[category][node_id]

    def agent_pos(self, agent_id: int, category: str):
        return self._agent_pos[category][agent_id]

    def create_edge(self, agent_1_id: int, category_1: str, agent_2_id: int, category_2: str,
                    **edge_properties):
        edge = self.edge_cls(category_1, agent_1_id,
                             category_2, agent_2_id,
                             edge_properties)
        src_pos = self.agent_pos(agent_1_id, category_1)
        dst_pos = self.agent_pos(agent_2_id, category_2)
        self.add_edge(src_pos, dst_pos, edge)

    def all_agents(self) -> List[int]:
        return self._nodes

    def all_agent_on_node(self, node_id) -> List[Tuple[str, int]]:
        l = []
        for category_name, ids_in_category in self._agent_ids.items():
            agent_ids = ids_in_category.get(node_id)
            if agent_ids is not None:
                l.extend([(category_name, agent_id) for agent_id in agent_ids])
        return l

    @classmethod
    def from_agent_containers(cls,
                              containers: 'Dict[str,AgentList]',
                              network_name: str = '',
                              network_params: dict = '',
                              builder: Callable = None):
        """
        :param containers: container or a list of container
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
        assert isinstance(containers, dict)
        node_id = 0
        for category, container in containers.items():
            assert isinstance(category, str)
            self.add_category(category)
            for agent in container:
                self.add_agent(agent.id, category, node_id)
                node_id += 1
        g = None
        if builder is not None:
            g = builder(self._nodes)
        else:
            if network_name == 'barabasi_albert_graph':
                g = nx.__getattribute__(network_name)(len(self._nodes), **network_params, )
            elif network_name == 'watts_strogatz_graph':
                g = nx.__getattribute__(network_name)(len(self._nodes), **network_params, )
            else:
                raise NotImplementedError(f"Network name {network_name} is not implemented!")
        print(g.edges)
        for edge in g.edges:
            agent_src = list(self.all_agent_on_node(edge[0]))[0]
            agent_dest = list(self.all_agent_on_node(edge[1]))[0]
            edge_obj = self.edge_cls(agent_src[0], agent_src[1], agent_dest[0], agent_dest[1], {})
            self.add_edge(edge[0], edge[1], edge_obj)
        return self


class NetworkDirected(OldNetwork):
    def __init__(self):
        super(NetworkDirected, self).__init__()

    def add_edge(self, source, target):
        pass

    def get_neighbors(self, node):
        pass
