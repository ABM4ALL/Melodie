import logging
import random
import time

import pandas as pd
from pandas.api.types import is_numeric_dtype, is_integer_dtype, is_float_dtype, is_string_dtype
import typing
from typing import TYPE_CHECKING, ClassVar, List, Dict, Union, Set, Optional, TypeVar, Type, Generic

from .basic import IndexedAgentList, MelodieExceptions, MelodieException
from collections.abc import Sequence
from .agent import Agent

AgentGeneric = TypeVar('AgentGeneric')
if TYPE_CHECKING:
    from .model import Model
    from .scenario_manager import Scenario

logger = logging.getLogger(__name__)


class BaseAgentContainer(Generic[AgentGeneric]):
    _ID_OFFSET = -1
    _agent_ids = set()

    def __init__(self):
        self.scenario: Union['Scenario', None] = None
        self.agents: Union[List['AgentGeneric'], Set['AgentGeneric'], None] = None

    @staticmethod
    def new_id():
        """
        Create a new ID
        :return:
        """
        BaseAgentContainer._ID_OFFSET += 1
        return BaseAgentContainer._ID_OFFSET

    def all_agent_ids(self) -> List[int]:
        """
        Get id of all agents.
        :return:
        """
        return [agent.id for agent in self.agents]

    def to_list(self, column_names: List[str] = None) -> List[Dict]:
        """
        Convert all agent properties to a list of dict.
        :param column_names:  property names
        :return:
        """

    def type_check(self, param_names: List[str], agent_params_df: pd.DataFrame):
        """
        Check if the agent is
        :param agent_sample:
        :param param_names:
        :param agent_params_df:
        :return:
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
                logger.warning(f"Cannot tell the type of column {col}.")
                dataframe_dtypes[col] = None
        for agent in self.agents:
            for param_name in param_names:
                param_type = type(getattr(agent, param_name))
                if param_type == dataframe_dtypes[param_name] or param_type is None:
                    continue
                else:
                    raise MelodieExceptions.Data.ObjectPropertyTypeUnMatchTheDataFrameError(param_name, param_type,
                                                                                            dataframe_dtypes, agent)

    def set_properties(self, props_df: pd.DataFrame):
        """
        Set parameters of all agents in current scenario.

        :return:
        """

        assert props_df is not None

        param_names = [param for param in props_df.columns if param not in
                       {'scenario_id'}]

        # props_df_cpy: Optional[pd.DataFrame] = None
        if "scenario_id" in props_df.columns:
            props_df_cpy = props_df.query(f"scenario_id == {self.scenario.id}").copy(True)
        else:
            props_df_cpy = props_df.copy()  # deep copy this dataframe.
        props_df_cpy.reset_index(drop=True, inplace=True)
        self.type_check(param_names, props_df_cpy)
        # props_df_cpy.set_index("id", inplace=True)
        # # Assign parameters to properties for each agent.
        for i, agent in enumerate(self.agents):
            params = {}
            for agent_param_name in param_names:
                # .item() method was applied to convert pandas/numpy data into python-builtin types.
                # 加一步判断，判断属性名称在Agent中存在，并且类型与setup()方法中定义的一致。
                params[agent_param_name] = props_df_cpy.loc[i, agent_param_name].item()

            agent.set_params(params)

    def post_setup(self):
        for i, agent in enumerate(self.agents):
            agent.post_setup()


class AgentList(BaseAgentContainer, Sequence, typing.Sequence[AgentGeneric]):

    def __init__(self, agent_class: ClassVar[AgentGeneric], length: int, model: 'Model') -> None:
        super(AgentList, self).__init__()
        self._iter_index = 0
        self.scenario = model.scenario
        self.agent_class: ClassVar[AgentGeneric] = agent_class
        self.initial_agent_num: int = length
        self.model = model
        self.agents: List[AgentGeneric] = self.init_agents()

    def __repr__(self):
        return f"<AgentList {self.agents}>"

    def __len__(self):
        return len(self.agents)

    def __getitem__(self, item) -> AgentGeneric:
        return self.agents.__getitem__(item)

    def __iter__(self):
        self._iter_index = 0
        return self

    def __next__(self) -> AgentGeneric:
        if self._iter_index < len(self.agents):
            elem = self.agents[self._iter_index]
            self._iter_index += 1
            return elem
        else:
            raise StopIteration

    def init_agents(self) -> List[AgentGeneric]:
        agents: List['AgentGeneric'] = [self.agent_class(BaseAgentContainer.new_id()) for i in
                                        range(self.initial_agent_num)]
        scenario = self.model.scenario
        for agent in agents:
            agent._scenario = scenario
            agent.setup()
        return IndexedAgentList(agents)

    def random_sample(self, sample_num: int) -> List['AgentGeneric']:
        return random.sample(self.agents, sample_num)

    def remove(self, agent: 'AgentGeneric'):
        for i, a in enumerate(self.agents):
            if a is agent:
                self.agents.pop(i)
                break

    def add(self, agent: 'AgentGeneric'):
        self.agents.add(agent)

    def to_list(self, column_names: List[str] = None) -> List[Dict]:
        protected_columns = ['id']
        data_list = []
        if len(self.agents) == 0:
            raise MelodieExceptions.Agents.AgentListEmpty(self)

        if column_names is None:
            column_names = list(self.__dict__.keys())
        column_names = protected_columns + column_names
        agent0 = self.agents[0]
        for column_name in column_names:
            if column_name not in agent0.__dict__.keys():
                raise MelodieExceptions.Agents.AgentPropertyNameNotExist(column_name, agent0)
        for agent in self.agents:
            d = {k: agent.__dict__[k] for k in column_names}
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
