# import random
import logging
import random
from typing import Any, Callable, TYPE_CHECKING

from .types import (
    ClassVar,
    List,
    Dict,
    Union,
    Set,
    TypeVar,
)

import pandas as pd

from .agent import Agent
from ..exceptions import MelodieExceptions, show_prettified_warning
from ..table import TABLE_TYPE, TableInterface

AgentGeneric = TypeVar("AgentGeneric")
logger = logging.getLogger("purepython-agent-list")


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


class BaseAgentContainer:
    """
    The base class that contains agents
    """

    def __init__(self):
        self._id_offset = -1
        self.scenario: Union["Scenario", None] = None
        self.agents: Union[List["AgentGeneric"], Set["AgentGeneric"], None] = None

    def new_id(self) -> int:
        """
        Create a new auto-increment ID
        """
        self._id_offset += 1
        return self._id_offset

    def all_agent_ids(self) -> List[int]:
        """
        Get id of all agents.
        """
        return [agent.id for agent in self]

    def to_list(self, column_names: List[str] = None) -> List[Dict]:
        """
        Convert all agent properties to a list of dict.

        :param column_names:  property names
        """

    def get_agent(self, agent_id: int) -> "AgentGeneric":
        raise NotImplementedError


class AgentList(BaseAgentContainer):
    def __init__(self, agent_class: "ClassVar[AgentGeneric]", model: "Model") -> None:
        super().__init__()
        self.scenario = model.scenario
        self.agent_class: "ClassVar[AgentGeneric]" = agent_class
        self.model = model
        self.indices = {}
        self.agents: List[AgentGeneric] = []

    def __repr__(self):
        return f"<AgentList {self.agents}>"

    def __len__(self):
        return len(self.agents)

    def __getitem__(self, item) -> AgentGeneric:
        return self.agents.__getitem__(item)

    def __iter__(self):
        return SeqIter(self.agents)

    def setup_agents(self, agents_num: int, params_df: TABLE_TYPE = None):
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

    def _set_index(self, agent_id, index):
        # print(deref(self.indices))
        self.indices[agent_id] = index

    def _get_index(self, agent_id):
        if agent_id in self.indices:
            return self.indices[agent_id]
        else:
            return -1

    def _setup(self):
        self.setup()

    def setup(self):
        """
        The setup method.

        If you would like to define custom AgentList, please be sure to inherit this method.
        """
        pass

    def init_agents(self) -> List[AgentGeneric]:
        """
        Initialize all agents in the container, and call the `setup()` method
        :return:
        """
        agents: List["AgentGeneric"] = [
            self.agent_class(self.new_id()) for i in range(self.initial_agent_num)
        ]
        scenario = self.model.scenario
        for agent in agents:
            agent.scenario = scenario
            agent.model = self.model
            agent.setup()
        return agents

    def random_sample(self, sample_num: int) -> List["AgentGeneric"]:
        """
        Randomly sample `sample_num` agents from the container
        :param sample_num:
        :return:
        """
        return random.sample(self.agents, sample_num)

    def _set_properties(self, props_table: TABLE_TYPE):
        """
        Set parameters of all agents in current scenario from a pandas dataframe.

        :return: None
        """
        table = TableInterface(props_table)

        param_names = [param for param in table.columns if param not in {"id_scenario"}]

        if "id_scenario" in table.columns:
            params_table = table.filter(
                lambda row: row["id_scenario"] == self.scenario.id
            )
        else:
            params_table = table  # deep copy this dataframe.
        if "id" in param_names:
            row: Dict[str, Any]
            for i, row in enumerate(params_table.iter_dicts()):
                params = {k: row[k] for k in param_names}
                agent = self.get_agent(params["id"])
                if agent is None:
                    agent = self.add()
                agent.set_params(params)
        else:
            row: Dict[str, Any]
            # params_table.df.data("out.csv")
            assert len(self) == len(params_table), (len(self), len(params_table))

            for i, row in enumerate(params_table.iter_dicts()):
                params = {k: row[k] for k in param_names}
                agent = self.agents(i)
                agent.set_params(params)

    def filter(self, condition: Callable[[AgentGeneric], bool]):
        """
        Filter agents satisfying the condition Callable[[Agent], bool]

        :return: a list of filtered agents
        """
        filtered_agents = []
        for agent in self.agents:
            if condition(agent):
                filtered_agents.append(agent)
        return filtered_agents

    def add(self, agent: "AgentGeneric" = None, params: Dict = None) -> "AgentGeneric":
        """
        Add an agent
        :param agent:
        :param params:
        :return:
        """
        return self._add(agent, params)

    def _add(self, agent, params):
        """
        Add an agent to this AgentList

        :param agent: Optional
        :param params: Optional
        :return:
        """
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
            if params.get("id") is not None:
                show_prettified_warning(
                    f"Warning, agent 'id'  {agent.id} passed in 'params' will be **overridden** by a new id {new_id} auto generated by {self.__class__.__name__}."
                )
            agent.set_params(params)
        agent.id = new_id
        self.agents.append(agent)

        self._set_index(agent.id, len(self.agents) - 1)
        return agent

    def set_properties(self, props_df: TABLE_TYPE):
        """
        Extract properties from a dataframe, and Each row in the dataframe represents the property of an agent.
        :param props_df:
        :return:
        """
        self._set_properties(props_df)
        self.agents.sort(key=lambda agent: agent.id)

    def to_list(self, column_names: List[str]) -> List[Dict]:
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
                raise MelodieExceptions.Agents.AgentPropertyNameNotExist(
                    column_name, agent0
                )
        for agent in self.agents:
            d = {k: getattr(agent, k) for k in column_names}
            d["id"] = agent.id
            data_list.append(d)
        return data_list

    def to_dataframe(self, column_names: List[str] = None) -> TABLE_TYPE:
        """
        Store all agent values to dataframe.
        This method is always called by the data collector.

        :param column_names: property names to store
        :return:
        """

        data_list = self.to_list(column_names)
        df = pd.DataFrame(data_list)
        df["id"] = df["id"].astype(int)
        return df

    def set_properties(self, props_df: TABLE_TYPE):
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

    def method_foreach(self, method_name, args):
        """
        For each agent, execute theirs method ``method_name`` with arguments ``args``

        :param method_name: Name of method, a ``str``;
        :param args: Arguments of a method, a ``tuple``
        :return: None
        """
        for agent in self.agents:
            getattr(agent, method_name)(*args)
            # method(agent, *args)

    def vectorize(self, prop_name):
        """
        NotImplemented yet.

        Generate an numpy array from this list, where the values come from the property defined by ``prop_name`` on each agent.

        :param prop_name: Property name
        :return: An 1-D Numpy array
        """
        if len(self.agents) == 0:
            return
        raise NotImplementedError

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

    # def type_check(self, param_names: List[str], agent_params_df: pd.DataFrame):
    #     """
    #     Check if the parameters in the data frame has corresponding type with param_name
    #
    #     :param param_names: Parameter names to be checked
    #     :param agent_params_df: Dataframe for agent initial parameters.
    #     :return: None
    #     """
    #     dtypes = agent_params_df.dtypes
    #     dataframe_dtypes = {}
    #     for col, dtype in dtypes.items():
    #         if is_integer_dtype(dtype):
    #             dataframe_dtypes[col] = int
    #         elif is_float_dtype(dtype):
    #             dataframe_dtypes[col] = float
    #         elif is_string_dtype(dtype):
    #             dataframe_dtypes[col] = str
    #         else:
    #             show_prettified_warning(f"Cannot tell the type of column {col}.")
    #             dataframe_dtypes[col] = None
    #     for agent in self:
    #         for param_name in param_names:
    #             # param_type = type(getattr(agent, param_name))
    #             param_type = type(getattr(agent, param_name))
    #             if param_type == dataframe_dtypes[param_name] or param_type is None:
    #                 continue
    #             else:
    #                 raise MelodieExceptions.Data.ObjectPropertyTypeUnMatchTheDataFrameError(param_name, param_type,
    #
    #                                                                                         __all__ = ['AgentList']
