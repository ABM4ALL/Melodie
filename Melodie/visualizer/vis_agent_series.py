from typing import Dict, List, Callable, Any

from .vis_charts import JSONBase
from .. import Agent


class AgentSeries(JSONBase):
    def __init__(
        self,
        name: str,
        type: str,
        role_getter,
        roles_repr,
        color: str = "",
        symbol="rect",
    ):
        self.name: str = name
        self.type: str = type
        self.data: List = []
        self._role_getter: Callable[["Agent"], int] = role_getter
        self._roles_repr: Dict[int, Dict[str, Any]] = roles_repr
        self.itemStyle: Dict = {
            "color": color,
        }
        self.symbol: str = symbol


class AgentSeriesManager(JSONBase):
    def __init__(self):
        self.agent_series: Dict[str, AgentSeries] = {}

    def add_series(
        self,
        series_name,
        series_type: str,
        role_getter: Callable[["Agent"], int],
        roles_repr,
        color: str = "",
        symbol: str = "",
    ):
        self.agent_series[series_name] = AgentSeries(
            series_name, series_type, role_getter, roles_repr
        )

    def set_series_data(self, series_name: str, data):
        self.agent_series[series_name].data = data

    def to_dict(self):
        return self.to_json()["agent_series"]
