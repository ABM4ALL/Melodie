import logging

from typing import Any, Callable, List, Dict, TYPE_CHECKING, Tuple, TypeVar, Union, Optional
from decimal import Decimal
from MelodieInfra.models.typeutils import REAL_NUM_TYPE
from MelodieInfra import JSONBase

logger = logging.getLogger(__name__)


def float_round(float_value):
    decimal_obj = Decimal.from_float(float_value)
    decimal_str = format(decimal_obj, '.6')
    return float(decimal_str)


def round_float_array(float_arr):
    return [float_round(v) for v in float_arr]


class ChartBase:

    def reset(self):
        pass

    def set_data_source(self, *args, **kwargs) -> Any:
        """
        Set the data source of chart

        :param args:
        :param kwargs:
        :return:
        """
        return self

    def update(self):
        pass


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

    def set_data_source(self, datasource: "Callable[[], Any]"):
        self._source = datasource

    def update(self, current_step: int):
        d = self._source()
        self.add_data_value(d)
        assert current_step == len(self.data), (current_step, len(self.data))


class Chart(JSONBase, ChartBase):
    def __init__(self):
        self._index = {}
        self.type = "line"
        self.series: Optional[List[ChartSeries]] = None

    def set_series(self, series_names: List[str]):
        self._index = {series_name: i for i, series_name in enumerate(series_names)}
        self.series: List[ChartSeries] = [ChartSeries(name) for name in series_names]
        return self

    def set_data_source(self, data_source: Dict[str, Callable[[], REAL_NUM_TYPE]]):
        """
        Set data source of each series

        :param data_source:
        :return:
        """
        self.set_series([k for k in data_source.keys()])
        for series_name in data_source.keys():
            # series = self.get_series(series_name)
            self.set_series_data_source(series_name, data_source[series_name])
        return self

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

    def get_series_data(self):
        chart_series_data = []
        for i in range(len(self.series)):
            s = {
                "name": self.get_series_by_index(i).seriesName,
                "value": self.get_series(
                    self.get_series_by_index(i).seriesName
                ).latest_data,
            }
            chart_series_data.append(s)
        return chart_series_data

    def set_series_data_source(self, series_name: str, datasource):
        """
        Set data source for one series

        :param series_name:
        :param datasource:
        :return:
        """
        self.get_series(series_name).set_data_source(datasource)
        return self


class CandleStickChart(Chart):

    def __init__(self):
        self.type = "candlestick"
        self._series_name = 'series'
        self.series: Tuple[ChartSeries] = (ChartSeries(self._series_name),)

    def get_series(self, series_name: str) -> ChartSeries:
        if series_name == self._series_name:
            return self.series[0]
        else:
            raise ValueError(series_name)

    def set_data_source(self, datasource: Callable[
        [], Tuple[REAL_NUM_TYPE, REAL_NUM_TYPE, REAL_NUM_TYPE, REAL_NUM_TYPE]]) -> 'CandleStickChart':
        """

        :param datasource: Callable, should return a tuple with four real number -- (open, close, low, high)
        :return:
        """
        self.get_series('series').set_data_source(datasource)
        return self

    def get_series_data(self):
        data = super().get_series_data()
        logger.warning(f"series data of candlestickchart {data}")
        if data[0]['value'] is None:
            pass
        else:
            assert len(data[0]['value']) == 4, \
                f"Data format error in data source of candlestick chart: {data[0]['value']}"
            data[0]['value'] = round_float_array(data[0]['value'])
        return data


class Gauge(JSONBase, ChartBase):
    def __init__(self, source: Callable[[], Union[int, float, Dict]]):
        self._sources: Dict[str, Callable[[], Union[int, float]]] = {}
        self.value: Dict[str, Union[int, float]] = {}

    def reset(self):
        pass

    def update(self, current_step):
        self.value = self._source()


class PieChart(JSONBase, ChartBase):
    def __init__(self):
        self.type = "pie"
        self._sources: Dict[str, Callable[[], Union[int, float]]] = {}
        self._source: Optional[Callable[[], Dict[Union[int, float]]]] = None
        self.value: Dict[str, Union[int, float]] = {}
        self._mode = 'single'

    def add_variable(self, variable_name: str, source: Callable[[], Union[int, float]]):
        self.value[variable_name] = 0
        self._sources[variable_name] = source

    def update(self, current_step):
        assert isinstance(self.value, dict)
        if self._mode == 'single':
            for varname in self._sources.keys():
                self.value[varname] = self._sources[varname]()
        else:
            self.value = self._source()

    def reset(self):
        self.value = {}

    def to_json(self):
        return {'type': self.type, 'series': self.get_series_data()}

    def get_series_data(self):
        return [{"name": k, 'value': v} for k, v in self.value.items()]


class BarChart(PieChart):
    def __init__(self):
        super(BarChart, self).__init__()
        self.type = 'bar'
        self._mode = 'single'

    def set_data_source(self, data_source: Dict[str, Callable[[], Union[int, float]]]):
        self._sources = data_source
        self._mode = 'single'
        return self

    def set_data_mutable_source(self, data_source: Callable[[], Dict[str, Union[int, float]]]):
        self._source = data_source
        self._mode = 'multi'
        return self


class ChartManager(JSONBase):
    def __init__(self):
        self.charts: Dict[str, Union[Chart, Gauge]] = {}

    def add_chart(self, chart_name: str, chart):
        self.charts[chart_name] = chart
        return chart

    def add_line_chart(self, chart_name: str) -> Chart:
        return self.add_chart(chart_name, Chart())

    def add_piechart(self, chart_name: str) -> PieChart:
        return self.add_chart(chart_name, PieChart())

    def add_barchart(self, chart_name: str) -> BarChart:
        return self.add_chart(chart_name, BarChart())

    def add_candlestick_chart(self, chart_name: str) -> CandleStickChart:
        return self.add_chart(chart_name, CandleStickChart())

    def all_chart_names(self):
        return set(self.charts.keys())

    def get_chart(self, chart_name: str) -> Chart:
        return self.charts[chart_name]

    def get_current_data(self) -> List[Dict[str, List]]:
        current_data = []
        for chart_name in self.all_chart_names():
            chart = self.get_chart(chart_name)
            current_data.append({"chartName": chart_name, "series": chart.get_series_data()})
        return current_data

    def reset(self):
        for chart_name, chart in self.charts.items():
            chart.reset()
        logger.info("Chart manager reset!")

    def update(self, current_step):
        for chart_name, chart in self.charts.items():
            chart.update(current_step)
