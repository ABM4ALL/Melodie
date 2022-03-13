import logging
import asyncio
import queue
from urllib.request import urlopen
from urllib.error import URLError
import threading
import time
import websockets
import json
from queue import Queue
from typing import Dict, Tuple, List, Any, Callable, Union, Set, TYPE_CHECKING
from websockets.legacy.server import WebSocketServerProtocol

from .basic.exceptions import MelodieExceptions
from .basic.vis_charts import ChartSeries, ChartManager, Chart

if TYPE_CHECKING:
    from Melodie import Scenario, BaseAgentContainer, Model, Grid
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Command code
STEP = 0
RESET = 1
CURRENT_DATA = 2
START = 3
GET_PARAMS = 4
SET_PARAMS = 5
INIT_OPTIONS = 6

UNCONFIGURED = 0
READY = 1
RUNNING = 2
FINISHED = 3

# Response status code
OK = 0
ERROR = 1

QUEUE_ELEM = Tuple[int, WebSocketServerProtocol]

MAX_ACTIVE_CONNECTIONS = 8
visualize_condition_queue_main = Queue(10)
visualize_result_queues: Dict[WebSocketServerProtocol, Queue] = {}

socks: Set[WebSocketServerProtocol] = set()


async def handler(ws: WebSocketServerProtocol, path):
    global socks
    if len(socks) >= MAX_ACTIVE_CONNECTIONS:
        await ws.send(
            json.dumps(
                {"type": "error", "step": 0,
                 "data": f"The number of connections exceeds the upper limit {MAX_ACTIVE_CONNECTIONS}. "
                         f"Please shutdown unused webpage or modify the limit.", "modelState": UNCONFIGURED,
                 "status": ERROR})
        )
        return
    socks.add(ws)
    visualize_result_queues[ws] = Queue(10)
    while 1:
        try:
            content = await asyncio.wait_for(ws.recv(), timeout=0.05)
            rec = json.loads(content)
            cmd = rec['cmd']
            data = rec['data']
            if 0 <= cmd <= 6:
                try:
                    visualize_condition_queue_main.put((cmd, data, ws), timeout=1)
                except:
                    import traceback
                    traceback.print_exc()
                    print("last_cmd_content", content)
            else:
                raise NotImplementedError(cmd)
        except (asyncio.TimeoutError, ConnectionRefusedError):
            pass
        if ws.closed:
            socks.remove(ws)
            visualize_result_queues.pop(ws)
            logger.info(f"websocket connection {ws} is going offline...")
            return
        try:
            while 1:
                res = visualize_result_queues[ws].get(False)
                await ws.send(res)
        except queue.Empty:
            pass


async def send_message(sock: WebSocketServerProtocol, msg):
    await sock.send(msg)


class MelodieModelReset(BaseException):
    def __init__(self, ws: WebSocketServerProtocol = None):
        self.ws = ws


class Visualizer:
    def __init__(self):
        self.current_step = 0
        self.model_state = UNCONFIGURED
        self.current_scenario: 'Scenario' = None
        self._model: 'Model' = None
        self.scenario_param: Dict[str, Union[int, str, float]] = {}

        self.chart_options: Dict[str, Any] = {}

        # self.plot_charts: Dict[str, List[ChartSeries]] = {}  # {<chartName>: ChartSeries[]}
        self.plot_charts: ChartManager = ChartManager()
        self.current_websocket: WebSocketServerProtocol = None

        start_server = websockets.serve(handler, 'localhost', 8765)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio_serve = asyncio.get_event_loop().run_forever

        self.th = threading.Thread(target=asyncio_serve)

        self.th.setDaemon(True)
        self.th.start()

    def setup(self):
        pass

    def reset(self):
        pass

    def format(self):
        pass

    @property
    def model(self):
        return self._model

    def add_plot_chart(self, chart_name: str, series_names: List[str]):
        if chart_name not in self.plot_charts.all_chart_names():
            self.plot_charts.add_chart(chart_name, series_names)
        else:
            raise ValueError(f"chart name '{chart_name}' already existed!")

    def set_chart_data_source(self, chart_name: str, series_name: str, source: "Callable[[Model], Union[int, float]]"):
        self.plot_charts.get_chart(chart_name).get_series(series_name).set_data_source(source)

    def set_plot_data(self, current_step: int, chart_name: str, series_values: Dict):
        """
        Set plot data
        :param chart_name:
        :param series_values:
        :return:
        """
        assert chart_name in self.plot_charts.all_chart_names()
        for series_name, series_value in series_values.items():
            series = self.plot_charts.get_chart(chart_name).get_series(series_name)
            series.add_data_value(series_value)
            assert current_step == len(series.data) - 1, (current_step, len(series.data))

    def send_initial_msg(self, ws: WebSocketServerProtocol):
        formatted = self.format()
        self.send_message(json.dumps(formatted))

    def send_message(self, msg):
        """
        Put message to the message queues of all active websocket connections.
        If the target queue is full, the message will be discarded.

        :param msg:
        :return:
        """
        closed_websockets: Set[WebSocketServerProtocol] = set()
        for ws, q in visualize_result_queues.items():
            if ws.closed:
                closed_websockets.add(ws)
                continue
            try:
                q.put(msg, timeout=1)
            except queue.Full:
                if ws.closed:
                    closed_websockets.add(ws)
        for closed_ws in closed_websockets:
            socks.remove(closed_ws)
            visualize_result_queues.pop(closed_ws)

    def send_chart_options(self):
        self.send_message(
            json.dumps(
                {"type": "initOption", "step": 0, "data": self.chart_options,
                 "modelState": self.model_state,
                 "status": OK}))

    def send_plot_series(self):
        self.send_message(
            json.dumps(
                {"type": "initPlotSeries",
                 "step": 0,
                 "data": self.plot_charts.to_json(),
                 "modelState": self.model_state,
                 "status": OK}))

    def send_scenario_params(self, params_list: List['Scenario.BaseParameter']):
        param_models = []
        initial_params = {}
        for param in params_list:
            initial_params[param.name] = {"value": param.init}
            param_models.append(param.to_dict())
        params = {
            "initialParams": initial_params,
            "paramModels": param_models
        }
        # print(params)
        self.send_message(
            json.dumps(
                {"type": "params", "step": self.current_step, "data": params, "modelState": self.model_state,
                 "status": OK}))
        # print(json.dumps(
        #     {"type": "params", "step": self.current_step, "data": params, "modelState": self.model_state, "status": OK},
        #     indent=4))

    def send_current_data(self):
        t0 = time.time()
        formatted = self.format()

        dumped = json.dumps(
            {"type": "data", "step": self.current_step, "data": formatted, "modelState": self.model_state,
             "status": OK})
        t1 = time.time()
        logger.info(f"Formatting current data takes:{t1 - t0} seconds")
        self.send_message(dumped)

    def send_error(self, err_msg):
        self.send_message(
            json.dumps({"type": "data", "step": self.current_step, "data": err_msg, "modelState": 10, "status": ERROR}))

    def get_in_queue(self) -> Tuple[int, Dict[str, Any], WebSocketServerProtocol]:
        """
        `while 1` statement was for checking the sigterm signal.
        :return:
        """
        while 1:
            try:
                res = visualize_condition_queue_main.get(timeout=1)
                handled = self.generic_handler(*res)
                assert isinstance(handled, bool)
                if not handled:
                    return res
                else:
                    pass
            except queue.Empty:
                pass

    def generic_handler(self, cmd_type: int, data: Dict[str, Any], ws: WebSocketServerProtocol) -> bool:
        """
        handler for viewing current data, get scenario parameters.
        :param cmd_type:
        :param data:
        :param ws:
        :return:
        """
        self.current_websocket = ws
        if cmd_type == GET_PARAMS:
            self.send_scenario_params(self.current_scenario.properties_as_parameters())
            return True
        elif cmd_type == RESET:
            self.scenario_param = {k: v['value'] for k, v in data['params'].items()}  #
            raise MelodieModelReset
        elif cmd_type == INIT_OPTIONS:
            self.send_chart_options()
            self.send_plot_series()
            return True
        else:
            return False

    def start(self):
        self.model_state = READY
        self.current_step = 0
        try:
            self.send_current_data()
        except:
            import traceback
            traceback.print_exc()

        while 1:
            logger.info("in start")
            flag, data, ws = self.get_in_queue()
            if flag in {STEP, CURRENT_DATA}:
                self.send_current_data()
                if flag == STEP:  # If the flag was step, then go to step No.1. So there should be one
                    # queue to put into the condition queue.
                    self.model_state = RUNNING
                    visualize_condition_queue_main.put((flag, {}, ws))
                    break
            else:
                self.send_error(f"Invalid command flag {flag} for function 'start'. ")

    def step(self, current_step):
        self.model_state = RUNNING
        self.current_step = current_step
        self.plot_charts.update(self.current_step)
        while 1:
            logger.info("in step")
            flag, data, ws = self.get_in_queue()
            if flag == STEP:
                self.send_current_data()
                break
            elif flag == CURRENT_DATA:
                self.send_current_data()
            else:
                self.send_error(f"Invalid command flag {flag} for function 'step'. ")

    def finish(self):
        self.model_state = FINISHED
        self.send_current_data()
        while 1:
            logger.info("in finish")
            flag, data, ws = self.get_in_queue()
            if flag == CURRENT_DATA:
                self.send_current_data()
            else:
                self.send_error(f"Invalid command flag {flag} for function 'finish'. ")


class GridVisualizer(Visualizer):
    def __init__(self):
        super().__init__()
        self.height = 0
        self.width = 0
        self.grid_roles = []

        self.grid_params = {}

        self.chart_options = {"animation": False, "progressiveThreshold": 100000, "tooltip": {"position": "top"},
                              "grid": {"height": "80%", "top": "10%"},
                              "xAxis": {"type": "category", "splitArea": {"show": True}},
                              "yAxis": {"type": "category", "splitArea": {"show": True}},
                              "visualMap": {
                                  "type": "piecewise",
                                  "categories": [1, 2, 3],
                                  "calculable": True,
                                  "orient": "horizontal",
                                  "left": "center",
                                  "inRange": {
                                      "color": {
                                          1: "#e33e33",
                                          2: "#fec42c",
                                          3: "#ff0000"
                                      }
                                  },
                                  "seriesIndex": [0]
                              },
                              "series": [
                                  {"universalTransition": {"enabled": False}, "name": "Spot", "type": "heatmap"}]
                              }
        self.other_series = {}
        try:
            my_url = urlopen("http://localhost:8089/api/tools/test")
        except ConnectionRefusedError:
            raise MelodieExceptions.Tools.MelodieStudioUnAvailable()
        except URLError:
            raise MelodieExceptions.Tools.MelodieStudioUnAvailable()

    def reset(self):
        self.grid_roles = []
        self.grid_params = {}
        self.plot_charts.reset()

    def convert_to_1d(self, x, y):
        return x * self.height + y

    def parse_series(self, grid: "Grid"):
        self.grid_roles = grid.get_roles().tolist()

        other_series_data = {}
        existed_agents = grid._existed_agents
        for category in existed_agents.keys():
            if other_series_data.get(category) is None:
                other_series_data[category] = []
            for agent_id in existed_agents[category]:
                pos = grid.get_agent_pos(agent_id, category)
                other_series_data[category].append({
                    'value': list(pos),
                    'id': agent_id,
                    'category': category,
                })
        for series_name, data in other_series_data.items():
            self.other_series[series_name]['data'] = data

    def parse_grid_roles(self, grid: "Grid", parser: Callable[['Spot'], int]):
        """
        Parse the role of each spot on the grid.

        :param grid: The grid object to parse
        :param parser: A function computes roles of each cell, returning an integer.
        :return:
        """
        self.width = grid.width
        self.height = grid.height
        self.grid_roles = [None] * (grid.height * grid.width)
        other_series_data = {}

        categories = grid._agent_ids.keys()
        for x in range(grid.width):
            for y in range(grid.height):
                spot = grid.get_spot(x, y)
                role = parser(spot)
                if role < 0:
                    self.grid_roles[self.convert_to_1d(x, y)] = [x, y, "-", 0]
                else:
                    self.grid_roles[self.convert_to_1d(x, y)] = [x, y, 1, role]
                for category in categories:
                    if other_series_data.get(category) is None:
                        other_series_data[category] = []
                    for agent_id in grid.get_agent_ids(category, x, y):
                        other_series_data[category].append({
                            'value': [x, y],
                            'id': agent_id,
                            'category': category,
                        })
        for series_name, data in other_series_data.items():
            self.other_series[series_name]['data'] = data

    def add_agent_series(self, series_name: str, series_type: str, color: str, symbol="rect", ):
        assert series_type in {'scatter'}
        self.other_series[series_name] = {
            "data": [],
            "itemStyle":
                {
                    "color": color,
                },
            "symbol": "rect",
            "type": series_type,
            "name": series_name,
        }

    def set_other_series_data(self, series_name, data):
        assert series_name in self.other_series
        self.other_series[series_name]['data'] = data

    def add_visualizer(self, type):
        pass


    def format(self):
        data = {
            "visualizers":
                [{
                    "name": "grid",
                    "type": "grid",
                    "data": {
                        "series":
                            [
                                {
                                    "data": self.grid_roles,
                                },
                            ]
                    }
                }],
            "plots": [{
                "chartName": name,
                "series": [
                    {
                        "name": self.plot_charts.get_chart(name).get_series_by_index(i).seriesName,
                        "value": self.plot_charts.get_chart(name).get_series(
                            self.plot_charts.get_chart(name).get_series_by_index(i).seriesName
                        ).latest_data} for i in range(len(self.plot_charts.get_chart(name).series))]}
                for name in self.plot_charts.all_chart_names()
            ]
        }
        data['visualizers'][0]['data']['series'].extend([series for k, series in self.other_series.items()])
        return data


class NetworkVisualizer(Visualizer):
    def __init__(self):
        super().__init__()

        logger.info("Network visualizer server is starting...")

        self.vertex_positions: Dict[str, Tuple[int, int]] = {}
        self.vertex_roles: Dict[str, int] = {}
        self.edge_roles: Dict[Tuple[int, int], int] = {}

        self.chart_options = {"title": {"text": "Graph"},
                              "tooltip": {},
                              "series": [
                                  {"type": "graphGL",
                                   "layout": "none",
                                   "animation": False,
                                   "symbolSize": 10,
                                   "symbol": "circle", "roam": True,
                                   "edgeSymbol": ["circle", "arrow"], "edgeSymbolSize": [4, 5],
                                   "itemStyle": {"opacity": 1},
                                   "categories": [
                                       {"name": 0, "itemStyle": {"color": "#67c23a"}},
                                       {"name": 1, "itemStyle": {"color": "#f56c6c"}}
                                   ]}]
                              }
        self.setup()

    def reset(self):
        self.edge_roles = {}
        self.vertex_roles = {}
        self.vertex_positions = {}

    def parse_edges(self, edges: List[Any], parser: Callable):

        for edge in edges:
            edge, pos = parser(edge)
            self.edge_roles[edge] = pos

    def parse_layout(self, node_info: List[Any],
                     parser: Callable[[Any], Tuple[Union[str, int], Tuple[float, float]]] = None):
        """

        :param node_info: A list contains a series of node information.
        :return:
        """
        if parser is None:
            parser = lambda node: (node['name'], (node['x'], node['y']))
        for node in node_info:
            node_name, pos = parser(node)
            self.vertex_positions[node_name] = pos

    def parse_role(self, node_info: List[Any],
                   parser: Callable[[Any], int] = None):
        """

        :param node_info: A list contains a series of node information.
        :return:
        """
        assert parser is not None
        for node in node_info:
            node_name, role = parser(node)
            assert isinstance(role, int), "The role of node should be an int."
            self.vertex_roles[node_name] = role

    def format(self):
        lst = []
        for name, pos in self.vertex_positions.items():
            lst.append(
                {
                    "name": name,
                    "x": pos[0],
                    "y": pos[1],
                    "category": self.vertex_roles[name]
                }
            )
        lst_edges = []
        for edge, role in self.edge_roles.items():
            lst_edges.append({
                "source": edge[0],
                "target": edge[1]
            })
        data = {
            "visualizer": {
                "series": [{
                    "data": lst,
                    "links": lst_edges
                }]
            },
            "plots": [{
                "chartName": name,
                "series": [
                    {
                        "name": self.plot_charts[name][i].seriesName,
                        "value": self.chart_data[name][self.plot_charts[name][i].seriesName][
                            self.current_step]} for i in
                    range(len(self.plot_charts[name]))]} for name in self.plot_charts.keys()
            ]
        }
        return data
