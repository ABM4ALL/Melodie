# cython:profile=True
# cython:language_level=3
# -*- coding:utf-8 -*-

import logging
import random
import pandas as pd
from pandas.api.types import is_integer_dtype, is_float_dtype, is_string_dtype
from typing import TYPE_CHECKING, Type, List, Dict, Union, Set, Optional, TypeVar, Type, Generic
from MelodieInfra.core.agent import Agent
from MelodieInfra import MelodieExceptions, MelodieException, show_prettified_warning

AgentGeneric = TypeVar('AgentGeneric')
if TYPE_CHECKING:
    from .model import Model
    from .scenario_manager import Scenario

logger = logging.getLogger(__name__)


def bs_key(agent):
    return agent.id


def _binary_search_agents(lis, num):
    left = 0
    right = len(lis) - 1
    mid = 0
    agent_id = 0
    while left <= right:
        mid = (left + right) // 2
        agent_id = bs_key(lis[mid])
        if num < agent_id:
            right = mid - 1
        elif num > agent_id:
            left = mid + 1
        else:
            return mid

    if mid == 0:
        return 0
    else:
        return -1


class SeqIter:
    """
    The iterator to deal with for-loops in AgentList or other agent containers
    """

    def __init__(self, seq):
        self._seq = seq
        self._i = 0

    def __next__(self):
        if self._i >= len(self._seq):
            raise StopIteration
        next_item = self._seq[self._i]
        self._i += 1
        return next_item


class DictIter:
    """
    The iterator to deal with for-loops in AgentList or other agent containers
    """

    def __init__(self, dic):
        self._dict = dic
        self._iter = iter(dic.items())

    def __next__(self):
        return next(self._iter)[1]


class BaseAgentContainer():
    """
    The base class that contains agents
    """

    def __init__(self):
        self._id_offset = -1
        self.scenario: Union['Scenario', None] = None

    def new_id(self):
        """
        Create a new auto-increment ID

        :return:
        """
        self._id_offset += 1
        return self._id_offset

    def to_list(self, column_names: List[str] = None) -> List[Dict]:
        """
        Convert all agent properties to a list of dict.
        
        :param column_names:  property names
        :return: None
        """

    def init_agents(self):
        """
        Initialize all agents in the container.

        During the initialization of agent, the ``setup()`` method of each agent will be called.

        :return: None
        """
        agents: List['AgentGeneric'] = [self.agent_class(self.new_id()) for i in
                                        range(self.initial_agent_num)]
        scenario = self.model.scenario

        for i, agent in enumerate(agents):
            agent.scenario = scenario
            agent.model = self.model
            agent.setup()
        return agents

    def _set_properties(self, props_df: pd.DataFrame):
        """
        Set parameters of all agents in current scenario from a pandas dataframe.

        :return: None
        """
        MelodieExceptions.Assertions.Type('props_df', props_df, pd.DataFrame)

        param_names = [param for param in props_df.columns if param not in
                       {'id_scenario'}]

        # props_df_cpy: Optional[pd.DataFrame] = None
        if "id_scenario" in props_df.columns:
            props_df_cpy = props_df.query(f"id_scenario == {self.scenario.id}").copy(True)
        else:
            props_df_cpy = props_df.copy()  # deep copy this dataframe.

        props_df_cpy.reset_index(drop=True, inplace=True)
        self.type_check(param_names, props_df_cpy)

        # Assign parameters to properties for each agent.
        for i, agent in enumerate(self):
            params = {}
            for agent_param_name in param_names:
                # .item() method was applied to convert pandas/numpy data into python-builtin types.
                item = props_df_cpy.loc[i, agent_param_name]
                if isinstance(item, str):
                    params[agent_param_name] = item
                else:
                    params[agent_param_name] = item.item()

            agent.set_params(params)

    def type_check(self, param_names: List[str], agent_params_df: pd.DataFrame):
        """
        Check if the parameters in the data frame has corresponding type with param_name

        :param param_names: Parameter names to be checked
        :param agent_params_df: Dataframe for agent initial parameters.
        :return: None
        """
        dtypes = agent_params_df.dtypes
        dataframe_dtypes = {}
        for col, dtype in dtypes.items():
            if is_integer_dtype(dtype):
                dataframe_dtypes[col] = int
            elif is_float_dtype(dtype):
                dataframe_dtypes[col] = float
            elif is_string_dtype(dtype):
                dataframe_dtypes[col] = str
            else:
                show_prettified_warning(f"Cannot tell the type of column {col}.")
                dataframe_dtypes[col] = None
        for agent in self:
            for param_name in param_names:
                # param_type = type(getattr(agent, param_name))
                param_type = type(getattr(agent, param_name))
                if param_type == dataframe_dtypes[param_name] or param_type is None:
                    continue
                else:
                    raise MelodieExceptions.Data.ObjectPropertyTypeUnMatchTheDataFrameError(param_name, param_type,
                                                                                            dataframe_dtypes, agent)


class AgentDict(BaseAgentContainer):
    def __init__(self, agent_class: Type[AgentGeneric], length: int, model: 'Model') -> None:
        super().__init__()
        self.scenario = model.scenario
        self.agent_class: Type[AgentGeneric] = agent_class
        self.initial_agent_num: int = length
        self.model = model
        self.agents = {agent.id: agent for agent in self.init_agents()}

    def __repr__(self):
        return f"<AgentList {self.agents}>"

    def __len__(self):
        return len(self.agents)

    def __getitem__(self, item):
        return self.agents.__getitem__(item)

    def __iter__(self):
        return DictIter(self.agents)

    def get_agent(self, agent_id):
        return self.agents.get(agent_id)

    def add(self, agent=None, params=None):
        self._add(agent, params)

    def _add(self, agent, params):
        new_id = self.new_id()
        if agent is not None:
            assert isinstance(agent, Agent)
        else:
            agent = self.agent_class(new_id)

        agent.scenario = self.model.scenario
        agent.model = self.model
        agent.setup()
        if params is not None:
            assert isinstance(params, dict)
            if params.get('id') is not None:
                show_prettified_warning(
                    f"Warning, agent 'id'  {agent.id} passed in 'params' will be **overridden** by a new id {new_id} auto generated by {self.__class__.__name__}."
                )
            agent.set_params(params)
        agent.id = new_id
        self.agents[agent.id] = agent

    def remove(self, agent):
        self.agents.pop(agent.id)

    def set_properties(self, props_df: pd.DataFrame):
        """
        Extract properties from a dataframe, and Each row in the dataframe represents the property of an agent.

        :param props_df:
        :return:
        """
        self._set_properties(props_df)


class AgentList(BaseAgentContainer):
    def __init__(self, agent_class: Type[AgentGeneric], model: 'Model') -> None:
        super(AgentList, self).__init__()
        self._iter_index = 0
        self.scenario = model.scenario
        self.agent_class: Type[AgentGeneric] = agent_class
        self.initial_agent_num: int = -1
        self.model = model
        self._map = {}
        self.indices = {}
        self.agents: List[AgentGeneric] = []

    def setup_agents(self, agents_num: int, params_df: pd.DataFrame = None):
        """
        Setup agents with specific number, and initialize their property by a dataframe if a dataframe is passed.

        :param agents_num: A integer.
        :param params_df : A pandas dataframe whose specification is the same as the argument of ``set_properties``
        :return:
        """
        self.initial_agent_num = agents_num
        self.agents = self.init_agents()
        for i, agent in enumerate(self.agents):
            self._set_index(agent.id, i)
        if params_df is not None:
            self.set_properties(params_df)

    def _setup(self):
        self.setup()

    def setup(self):
        """
        The setup method.

        If you would like to define custom AgentList, please be sure to inherit this method.
        """
        pass

    def __repr__(self):
        return f"<AgentList {self.agents}>"

    def __len__(self):
        return len(self.agents)

    def __getitem__(self, item) -> AgentGeneric:
        return self.agents.__getitem__(item)

    def __iter__(self):
        self._iter_index = 0
        return SeqIter(self.agents)

    def random_sample(self, sample_num: int) -> List['AgentGeneric']:
        """
        Randomly sample ``sample_num`` agents from the container
        
        :param sample_num:
        :return:
        """
        return random.sample(self.agents, sample_num)

    def remove(self, agent):
        """
        Remove an agent from the AgentList

        :param agent:
        :return:
        """
        # print(deref(self.indices))
        index = self._get_index(agent.id)

        self.agents.pop(index)

        for i, a in enumerate(self.agents):
            self._set_index(a.id, i)

    def _set_index(self, agent_id, index):
        # print(deref(self.indices))
        self.indices[agent_id] = index

    def _get_index(self, agent_id):
        # cpp_map[long, long] * indices = self.indices
        # print("addr of indices:",<uintptr_t>&indices,<uintptr_t>&deref(self.indices), <uintptr_t>self.indices)
        # cnt = self.indices.count(agent_id)
        if agent_id in self.indices:
            return self.indices[agent_id]
        else:
        # if cnt < 1:
            raise IndexError("Index error occurred in the get_index")
        # else:
        #     return self.indices.at(agent_id)

    def filter(self, condition):
        """
        Filter agents satisfying the condition Callable[[Agent], bool]

        :return: a list of filtered agents
        """
        filtered_agents = []
        for agent in self.agents:
            if condition(agent):
                filtered_agents.append(agent)
        return filtered_agents

    def add(self, agent=None, params=None) -> None:
        """
        Add an agent onto this agent list.

        Notice:

        1. The ``agent`` object should have the same type as this agent list's ``agent_class``.
        2. The ``id`` of new agent will be overriden by an auto-increment number.


        :param agent: If None, an agent of corresponding type will be automatically created.
        :return: None
        """
        self._add(agent, params)

    def _add(self, agent, params):
        """
        Add an agent to this AgentList

        :param agent: Optional
        :param params: Optional
        :return:
        """
        new_id = self.new_id()
        if agent is not None:
            assert isinstance(agent, Agent), agent
        else:
            agent = self.agent_class(new_id)

        agent.scenario = self.model.scenario
        agent.model = self.model
        agent.setup()
        if params is not None:
            assert isinstance(params, dict)
            if params.get('id') is not None:
                show_prettified_warning(
                    f"Warning, agent 'id'  {agent.id} passed in 'params' will be **overridden** by a new id {new_id} auto generated by {self.__class__.__name__}."
                )
            agent.set_params(params)
        agent.id = new_id
        self.agents.append(agent)

        self._set_index(agent.id, len(self.agents) - 1)

    def to_json(self):
        """
        Convert agent list to a json.

        """
        return [agent.to_json() for agent in self.agents]

    def to_list(self, column_names: List[str] = None) -> List[Dict]:
        """
        Dump all agent and their properties into a list of dict.

        :param column_names:  The property names to be dumped.
        :return:
        """

        data_list = []
        if len(self.agents) == 0:
            raise MelodieExceptions.Agents.AgentListEmpty(self)

        agent0 = self.agents[0]

        for column_name in column_names:
            if not hasattr(agent0, column_name):
                raise MelodieExceptions.Agents.AgentPropertyNameNotExist(column_name, agent0)
        for agent in self.agents:
            d = {k: getattr(agent, k) for k in column_names}
            d['id'] = agent.id
            data_list.append(d)
        return data_list

    def to_dataframe(self, column_names: List[str] = None) -> pd.DataFrame:
        """
        Store all agent values to dataframe.
        This method is always called by the data collector.

        :param column_names: property names to store
        :return:
        """
        data_list = self.to_list(column_names)
        df = pd.DataFrame(data_list)
        df['id'] = df['id'].astype(int)
        return df

    def set_properties(self, props_df: pd.DataFrame):
        """
        Extract properties from a dataframe, and Each row in the dataframe represents the property of an agent.

        For example, if there are 100 agents with ``id`` from 0 to 99, and each agent contains properties ``a: int`` and ``b: float``,
        the ``props_df`` could be like this:


        .. code-block:: python

            import random
            import pandas as pd

            df = pd.DataFrame([{"id": i, "a": 2, "b": random.random()} for i in range(100)])
            print(df.head())

        The output is(df has 100 rows):

        .. code-block:: sh

                id  a         b
            0    0  2  0.207738
            1    1  2  0.236711
            2    2  2  0.869793
            3    3  2  0.797763
            4    4  2  0.900024

        For each scenario, same parameter values inside props_df will be assigned to each agents.
        As an instance, properties ``b`` value at ``agent 0`` in both ``scenario 0`` and ``1`` are both ``0.207738``.

        To set different initial parameters for different scenarios, please add a new column ``id_scenario``.
        An example of dataframe structure is shown below, and in this case, ``b`` of ``agent 0`` in ``scenario 0`` is ``0.207738``,
        while in ``scenario 1`` it was ``0.778997``

        .. code-block:: sh

                id_scenario  id  a         b
            0             0   0  2  0.207738
            1             0   1  2  0.236711
            2             0   2  2  0.869793
            ......
            100           1   0  2  0.778997
            101           1   1  2  0.450674


        :param props_df: ``pd.DataFrame`` containing agent initial properties.
        :return:
        """
        self._set_properties(props_df)
        self.agents.sort(key=lambda agent: agent.id)

    def all_agent_ids(self) -> List[int]:
        """
        Get ``id`` of all agents.

        :return: A ``list`` of ``int``.
        """
        return [agent.id for agent in self.agents]

    # cpdef get_agent(self, long agent_id):
    #     """
    #     Get an agent from the agent list

    #     :param agent_id:
    #     """
    #     index = _binary_search_agents(self.agents, agent_id)
    #     if index == -1:
    #         return None
    #     else:
    #         return self.agents[index]

    def get_agent(self, agent_id):
        """
        Get an agent from the agent list. If agent unexist, return None.

        :param agent_id: The id of the agent object.
        :return: An agent object, or None.
        """
        index = self._get_index(agent_id)
        if index == -1:
            return None
        else:
            return self.agents[index]

    # @cython.nonecheck(False)
    # @cython.boundscheck(False)
    def method_foreach(self, method_name, args):
        """
        For each agent, execute theirs method ``method_name`` with arguments ``args``

        :param method_name: Name of method, a ``str``;
        :param args: Arguments of a method, a ``tuple``
        :return: None
        """
        method = getattr(self.agent_class, method_name)
        # cdef Agent agent
        agent_num = len(self.agents)
        # cdef PyObject* ptr

        for i in range(agent_num):
            agent = self.agents[i]
            method(agent, *args)

    def vectorize(self, prop_name: str):
        """
        NotImplemented yet.

        Generate an numpy array from this list, where the values come from the property defined by ``prop_name`` on each agent.

        :param prop_name: Property name
        :return: An 1-D Numpy array
        """
        if len(self.agents) == 0:
            return
        raise NotImplementedError
