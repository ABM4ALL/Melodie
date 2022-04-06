from typing import Callable, List, Dict, Tuple, TYPE_CHECKING, Union, Optional

if TYPE_CHECKING:
    from Melodie import Model

import logging

logger = logging.getLogger(__name__)


class JSONBase:
    def to_json(self):
        d = {}
        for k, v in self.__dict__.items():
            if k.startswith("_"):
                continue
            elif hasattr(v, "to_json"):
                d[k] = v.to_json()
            elif isinstance(v, dict):
                new_dict = {}
                for new_k, new_v in v.items():
                    if hasattr(new_v, "to_json"):
                        new_dict[new_k] = new_v.to_json()
                    else:
                        new_dict[new_k] = new_v
                d[k] = new_dict
            elif isinstance(v, (list, tuple)):
                new_list = []
                for new_v in v:
                    if hasattr(new_v, "to_json"):
                        new_list.append(new_v.to_json())
                    else:
                        new_list.append(new_v)
                d[k] = new_list
            else:
                d[k] = v
        return d


class ChartSeries(JSONBase):
    def __init__(self, name: str, source: "Callable[[], int]" = None):
        self.seriesName = name
        self._source = source
        self.data: List[Union[int, float]] = []
        self.latest_data: Optional[Union[int, float]] = None

    def add_data_value(self, data_value: Union[int, float]):
        self.latest_data = data_value
        self.data.append(data_value)

    def reset(self):
        self.data = []
        self.latest_data = None

    def set_data_source(self, datasource: "Callable[[], int]"):
        self._source = datasource

    def update(self, current_step: int):
        d = self._source()
        self.add_data_value(d)
        assert current_step == len(self.data), (current_step, len(self.data))


class Chart(JSONBase):
    def __init__(self, series_names: List[str]):
        self._index = {series_name: i for i, series_name in enumerate(series_names)}
        self.series: Tuple[ChartSeries] = tuple([ChartSeries(name) for name in series_names])

    def get_series(self, series_name: str) -> ChartSeries:
        return self.series[self._index[series_name]]

    def get_series_by_index(self, series_index: int) -> ChartSeries:
        return self.series[series_index]

    def reset(self):
        for series in self.series:
            series.reset()

    def update(self, current_step: int):
        for series in self.series:
            series.update(current_step)


class ChartManager(JSONBase):
    def __init__(self):
        self.charts: Dict[str, Chart] = {}

    def add_chart(self, chart_name: str, series_names: List[str]):
        self.charts[chart_name] = Chart(series_names)

    def all_chart_names(self):
        return set(self.charts.keys())

    def get_chart(self, chart_name: str) -> Chart:
        return self.charts[chart_name]

    def get_current_data(self) -> List[Dict[str, List]]:
        current_data = []
        for chart_name in self.all_chart_names():
            chart = self.get_chart(chart_name)
            chart_series_data = []
            for i in range(len(chart.series)):
                s = {
                    "name": chart.get_series_by_index(i).seriesName,
                    "value": chart.get_series(
                        chart.get_series_by_index(i).seriesName
                    ).latest_data}
                chart_series_data.append(s)
            current_data.append({
                "chartName": chart_name,
                "series": chart_series_data
            })
        return current_data

    def reset(self):
        for chart_name, chart in self.charts.items():
            chart.reset()
        logger.info("Chart manager reset!")

    def update(self, current_step):
        for chart_name, chart in self.charts.items():
            chart.update(current_step)
