from typing import Dict, List

from .vis_charts import JSONBase


class AgentSeries(JSONBase):
    def __init__(self, name: str, type: str, color: str, symbol="rect"):
        self.name: str = name
        self.type: str = type
        self.data: List = []
        self.itemStyle: Dict = {
            "color": color,
        }
        self.symbol: str = symbol


class AgentSeriesManager(JSONBase):
    def __init__(self):
        self.agent_series: Dict[str, AgentSeries] = {}

    def add_series(self, series_name, series_type: str, color: str, symbol: str):
        self.agent_series[series_name] = AgentSeries(
            series_name, series_type, color, symbol
        )

    def set_series_data(self, series_name: str, data):
        self.agent_series[series_name].data = data

    def to_dict(self):
        return self.to_json()["agent_series"]
