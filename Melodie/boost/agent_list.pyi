from Melodie import Model, Scenario
import pandas as pd
import typing
from typing import (
    Callable,
    List,
    Dict,
    Union,
    Set,
    Optional,
    TypeVar,
    Generic,
    Iterable,
)

from collections.abc import Sequence

AgentGeneric = TypeVar("AgentGeneric")
ContainerGeneric = TypeVar("ContainerGeneric")

class SeqIter(Generic[AgentGeneric]):
    def __init__(self, seq: Iterable[AgentGeneric]):
        self._seq = seq
        self._i = 0
    def __next__(self) -> AgentGeneric: ...

class BaseAgentContainer(Iterable[Generic[AgentGeneric]]):
    _agent_ids = set()

    def __init__(self):
        self._id_offset = -1
        self.scenario: Union[Scenario, None] = None
        self.agents: Union[List[AgentGeneric], Set[AgentGeneric], None] = None
    def __iter__(self) -> Generic[AgentGeneric]: ...
    def new_id(self) -> int: ...
    def all_agent_ids(self) -> List[int]: ...
    def to_list(self, column_names: List[str] = None) -> List[Dict]: ...
    def type_check(self, param_names: List[str], agent_params_df: pd.DataFrame): ...
    def set_properties(self, props_df: pd.DataFrame) -> None: ...
    def get_agent(self, agent_id: int) -> Optional[AgentGeneric]: ...

class AgentDict(BaseAgentContainer):
    pass

class AgentList(BaseAgentContainer, Sequence, typing.Sequence[AgentGeneric]):
    def __init__(self, agent_class: typing.Type[AgentGeneric], model: "Model") -> None:
        super(AgentList, self).__init__()
        self._iter_index = 0
        self.scenario = model.scenario
        self.agent_class: typing.Type[AgentGeneric] = agent_class
        self.initial_agent_num: int = -1
        self.model = model
        self.agents: List[AgentGeneric] = self.init_agents()
    def __repr__(self):
        return f"<AgentList {self.agents}>"
    def __len__(self):
        return len(self.agents)
    def __getitem__(self, item) -> AgentGeneric:
        return self.agents.__getitem__(item)
    def __iter__(self) -> SeqIter: ...
    def setup(self) -> None: ...
    def init_agents(self) -> List[AgentGeneric]: ...
    def setup_agents(self, agents_num: int, params_df: pd.DataFrame = None): ...
    def random_sample(self, sample_num: int) -> List["AgentGeneric"]: ...
    def remove(self, agent: "AgentGeneric") -> None: ...
    def add(self, agent: "AgentGeneric" = None, params: Dict = None) -> None: ...
    def to_list(self, column_names: List[str] = None) -> List[Dict]: ...
    def to_dataframe(self, column_names: List[str] = None) -> pd.DataFrame: ...
    def set_properties(self, props_df: pd.DataFrame): ...
    def filter(
        self, condition: Callable[["AgentGeneric"], bool]
    ) -> List["AgentGeneric"]: ...
