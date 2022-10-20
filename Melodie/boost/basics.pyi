from typing import Any, Optional, TYPE_CHECKING, Dict, List

import pandas as pd

if TYPE_CHECKING:
    from Melodie.model import Model
    from Melodie.scenario_manager import Scenario

class Element:
    def set_params(self, params: Dict[str, Any]): ...

class Agent(Element):
    def __init__(self, agent_id: int):
        self.id = agent_id
        self.scenario: Optional["Scenario"] = None
        self.model: Optional["Model"] = None
    def setup(self):
        pass
    def __repr__(self) -> str: ...
    def set_params(self, params: Dict[str, Any]): ...
    def get_style(self): ...
    def to_dict(self, attributes: List[str]): ...

class Environment(Element):
    def __init__(self):
        self.model: Optional["Model"] = None
        self.scenario: Optional["Scenario"] = None
    def setup(self) -> None: ...
    def to_dict(self, properties: List[str]) -> Dict: ...
    def to_dataframe(self, properties: List[str]) -> pd.DataFrame: ...
    def _setup(self) -> None: ...
