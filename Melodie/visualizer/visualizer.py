import logging
import asyncio
import queue
from copy import deepcopy
from urllib.request import urlopen
from urllib.error import URLError
import threading
import time
import websockets
import json
from queue import Queue
from typing import Dict, Tuple, List, Any, Callable, Union, Set, TYPE_CHECKING, Optional

from websockets.exceptions import ConnectionClosedOK
from websockets.legacy.server import WebSocketServerProtocol

from ..utils import MelodieExceptions
from .vis_agent_series import AgentSeriesManager
from .vis_charts import ChartManager
from ..boost.grid import Spot

if TYPE_CHECKING:
    from Melodie import Scenario, Model, Grid, Network, Agent, AgentList

    ComponentType = Union[Grid, Network]
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
                {
                    "type": "error",
                    "period": 0,
                    "data": f"The number of connections exceeds the upper limit {MAX_ACTIVE_CONNECTIONS}. "
                    f"Please shutdown unused webpage or modify the limit.",
                    "modelState": UNCONFIGURED,
                    "status": ERROR,
                }
            )
        )
        return
    socks.add(ws)
    visualize_result_queues[ws] = Queue(10)
    while 1:
        try:
            content = await asyncio.wait_for(ws.recv(), timeout=0.05)
            rec = json.loads(content)
            cmd = rec["cmd"]
            data = rec["data"]
            if 0 <= cmd <= 6:
                try:
                    visualize_condition_queue_main.put((cmd, data, ws), timeout=1)
                except:
                    import traceback

                    traceback.print_exc()
            else:
                raise NotImplementedError(cmd)
        except (asyncio.TimeoutError, ConnectionRefusedError):
            pass
        except ConnectionClosedOK as e:
            logger.info(e.reason)
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


def execute_only_enabled(func):
    """
    Execute the decorated function only if the Visualizer.enabled() is True.

    :param func:
    :return:
    """

    def wrapper(*args, **kwargs):
        if Visualizer.enabled:
            return func(*args, **kwargs)

    return wrapper


class Visualizer:
    enabled = True  # If in the Simulator.run() or Simulator.run_parallel(), this flag will be set to False
    ws_port = 8765  # The websocket port that is desired to transfer data.

    def __init__(self):
        self.current_step = 0
        self.model_state = UNCONFIGURED
        self.current_scenario: "Scenario" = None
        self._model: "Model" = None
        self.scenario_param: Dict[str, Union[int, str, float]] = {}
        self.visualizer_components: List[
            Tuple["ComponentType", str, Dict, Dict, Callable[["Agent"], int]]
        ] = []

        self.plot_charts: ChartManager = ChartManager()
        self.agent_series_managers: Dict[str, AgentSeriesManager] = {}
        self.agent_lists: Dict[int, "AgentList"] = {}

        self.current_websocket: Optional[WebSocketServerProtocol] = None
        self.th: Optional[threading.Thread] = None

        self.start_websocket()

    @execute_only_enabled
    def start_websocket(self):
        start_server = websockets.serve(handler, "localhost", self.ws_port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio_serve = asyncio.get_event_loop().run_forever

        self.th = threading.Thread(target=asyncio_serve)

        self.th.setDaemon(True)
        self.th.start()

        try:
            urlopen("http://localhost:8089/api/tools/test")
        except ConnectionRefusedError:
            raise MelodieExceptions.Tools.MelodieStudioUnAvailable()
        except URLError:
            raise MelodieExceptions.Tools.MelodieStudioUnAvailable()

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

    def set_chart_data_source(
        self,
        chart_name: str,
        series_name: str,
        source: "Callable[[Model], Union[int, float]]",
    ):
        self.plot_charts.get_chart(chart_name).get_series(series_name).set_data_source(
            source
        )

    def set_plot_data(self, current_step: int, chart_name: str, series_values: Dict):
        """
        Set plot data
        :param current_step:
        :param chart_name:
        :param series_values:
        :return:
        """
        MelodieExceptions.Visualizer.Charts.ChartNameAlreadyDefined(
            chart_name, self.plot_charts.all_chart_names()
        )
        for series_name, series_value in series_values.items():
            series = self.plot_charts.get_chart(chart_name).get_series(series_name)
            series.add_data_value(series_value)
            assert current_step == len(series.data) - 1, (
                current_step,
                len(series.data),
            )

    def _re_init(self):
        self.agent_series_managers = {}
        self.plot_charts = self.plot_charts
        self.scenario_param = {}
        self.visualizer_components = []

    def set_model(self, model: "Model"):
        """
        Set model of visualizer. This is called every time the model resets

        :param model:
        :return:
        """
        self._model = model
        model._setup()
        self._re_init()
        self._model.init_visualize()

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

    def get_visualizers_initial_options(self):
        initial_options = []
        for (
            component_name,
            component_type,
            options,
            _1,
            _2,
        ) in self.visualizer_components:
            if component_type == "grid":
                initial_options.append(options)
            else:
                raise NotImplementedError
        return initial_options

    def send_chart_options(self):
        self.send_message(
            json.dumps(
                {
                    "type": "initOption",
                    "period": 0,
                    "data": self.get_visualizers_initial_options(),
                    "modelState": self.model_state,
                    "status": OK,
                }
            )
        )

    def send_plot_series(self):
        print(self.plot_charts.to_json())
        self.send_message(
            json.dumps(
                {
                    "type": "initPlotSeries",
                    "period": 0,
                    "data": self.plot_charts.to_json(),
                    "modelState": self.model_state,
                    "status": OK,
                }
            )
        )

    def send_scenario_params(self, params_list: List["Scenario.BaseParameter"]):
        param_models = []
        initial_params = {}
        for param in params_list:
            initial_params[param.name] = {"value": param.init}
            param_models.append(param.to_dict())
        params = {"initialParams": initial_params, "paramModels": param_models}

        self.send_message(
            json.dumps(
                {
                    "type": "params",
                    "period": self.current_step,
                    "data": params,
                    "modelState": self.model_state,
                    "status": OK,
                }
            )
        )

    def send_current_data(self):
        t0 = time.time()
        formatted = self.format()

        dumped = json.dumps(
            {
                "type": "data",
                "period": self.current_step,
                "data": formatted,
                "modelState": self.model_state,
                "status": OK,
            }
        )
        t1 = time.time()
        logger.info(f"Formatting current data takes:{t1 - t0} seconds")
        self.send_message(dumped)

    def send_error(self, err_msg):
        self.send_message(
            json.dumps(
                {
                    "type": "data",
                    "period": self.current_step,
                    "data": err_msg,
                    "modelState": 10,
                    "status": ERROR,
                }
            )
        )

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

    def generic_handler(
        self, cmd_type: int, data: Dict[str, Any], ws: WebSocketServerProtocol
    ) -> bool:
        """
        The handler for viewing current data, getting scenario parameters.
        :param cmd_type:
        :param data:
        :param ws:
        :return:
        """
        self.current_websocket = ws
        if cmd_type == GET_PARAMS:
            self.send_scenario_params(self.current_scenario.get_parameters())
            return True
        elif cmd_type == RESET:
            self.scenario_param = {k: v["value"] for k, v in data["params"].items()}  #
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
        self.reset()
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
                if (
                    flag == STEP
                ):  # If the flag was period, then go to period No.1. So there should be one
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
            logger.info("in period")
            flag, data, ws = self.get_in_queue()
            if flag == STEP:
                self.send_current_data()
                break
            elif flag == CURRENT_DATA:
                self.send_current_data()
            else:
                self.send_error(f"Invalid command flag {flag} for function 'period'. ")

    def finish(self):
        self.model_state = FINISHED
        self.send_current_data()
        while 1:
            logger.info("in finish")
            flag, data, ws = self.get_in_queue()
            if flag == CURRENT_DATA:
                self.send_current_data()
            else:
                if flag == STEP:
                    self.send_error(f"Model already finished, please reset the model.")
                else:
                    self.send_error(
                        f"Invalid command flag {flag} for function 'finish'. "
                    )


class GridVisualizer(Visualizer):
    def __init__(self):
        super().__init__()
        self.height = 0
        self.width = 0

        self.grid_roles = []

        self.grid_params = {}

    def reset(self):
        self.grid_roles = []
        self.grid_params = {}
        self.plot_charts.reset()

    def convert_to_1d(self, x, y):
        return x * self.height + y

    def parse_grid_series(self, grid: "Grid"):

        agents_vis_dicts = []
        spots = []

        spot_attributes = ["id", "x", "y"] + list(grid.get_spot(0, 0).__dict__.keys())
        if type(grid.get_spot(0, 0)) == Spot:
            for x in range(grid.width()):
                for y in range(grid.height()):
                    spot = grid.get_spot(x, y)
                    spots.append(
                        {
                            "data": spot.to_dict(spot_attributes),
                            "style": spot.get_style(),
                        }
                    )
        for agent_list_name, agent_list in self.agent_lists.items():
            if len(agent_list) == 0:
                continue
            first_agent = agent_list[0]
            attributes = ["id", "x", "y", "category"] + list(
                first_agent.__dict__.keys()
            )
            for agent in agent_list:
                agents_vis_dicts.append(
                    {"data": agent.to_dict(attributes), "style": agent.get_style()}
                )
        return {
            "name": "grid",
            "type": "grid",
            "agents": agents_vis_dicts,
            "spots": spots,
        }

    def add_agent_series(
        self,
        component_name: str,
        series_id: int,
        agent_container: Union["AgentList"],
        role_getter: Callable[["Agent"], int] = None,
        roles_repr: Dict = None,
        series_type: str = "scatter",
        color: str = "#000000",
        symbol="rect",
    ):
        if series_type not in {"scatter"}:
            MelodieExceptions.Program.Variable.VariableNotInSet(
                "series_type", series_type, {"scatter"}
            )
        if component_name not in self.agent_series_managers:
            self.agent_series_managers[component_name] = AgentSeriesManager()
        self.agent_series_managers[component_name].add_series(
            series_id, series_type, role_getter, roles_repr, color, symbol
        )
        self.agent_lists[series_id] = agent_container

    def add_visualize_component(
        self,
        name: str,
        component: "ComponentType",
        color_categories: Dict[int, str],
        agent_roles: Dict[int, Dict[str, Any]],
        roles_getter: Callable[["Agent"], int],
    ):
        from ..boost.grid import Grid
        from ..network import Network

        MelodieExceptions.Assertions.Type(
            f'argument "component"', component, (Grid, Network)
        )

        chart_options = {
            "animation": False,
            "progressiveThreshold": 100000,
            "tooltip": {"position": "top"},
            "grid": {"height": "80%", "top": "10%"},
            "xAxis": {"type": "category", "splitArea": {"show": True}},
            "yAxis": {"type": "category", "splitArea": {"show": True}},
            "visualMap": {
                "type": "piecewise",
                "categories": [i for i, color in color_categories.items()],
                "calculable": True,
                "orient": "horizontal",
                "left": "center",
                "inRange": {"color": deepcopy(color_categories)},
                "seriesIndex": [0],
            },
            "series": [
                {
                    "universalTransition": {"enabled": False},
                    "name": "Spot",
                    "type": "heatmap",
                }
            ],
            "name": name,
            "columns": component.width(),
            "rows": component.height(),
        }
        self.visualizer_components.append(
            (component, name, chart_options, agent_roles, roles_getter)
        )

    def format(self):
        from ..boost.grid import Grid

        visualizers = []
        for (
            vis_component,
            vis_component_name,
            _1,
            agent_roles,
            roles_getter,
        ) in self.visualizer_components:
            if isinstance(vis_component, Grid):
                r = self.parse_grid_series(vis_component)
                visualizers.append(r)
            else:
                raise NotImplementedError
        data = {
            "visualizers": visualizers,
            "plots": self.plot_charts.get_current_data(),
        }

        return data


class NetworkVisualizer(Visualizer):
    def __init__(self):
        super().__init__()

        logger.info("Network visualizer server is starting...")

        self.vertex_positions: Dict[str, Tuple[int, int]] = {}
        self.vertex_roles: Dict[str, int] = {}
        self.edge_roles: Dict[Tuple[int, int], int] = {}

        self.chart_options = {
            "title": {"text": "Graph"},
            "tooltip": {},
            "series": [
                {
                    "type": "graphGL",
                    "layout": "none",
                    "animation": False,
                    "symbolSize": 10,
                    "symbol": "circle",
                    "roam": True,
                    "edgeSymbol": ["circle", "arrow"],
                    "edgeSymbolSize": [4, 5],
                    "itemStyle": {"opacity": 1},
                    "categories": [
                        {"name": 0, "itemStyle": {"color": "#67c23a"}},
                        {"name": 1, "itemStyle": {"color": "#f56c6c"}},
                    ],
                }
            ],
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

    def parse_layout(
        self,
        node_info: List[Any],
        parser: Callable[[Any], Tuple[Union[str, int], Tuple[float, float]]] = None,
    ):
        """

        :param node_info: A list contains a series of node information.
        :param parser: The layout of the network.
        :return:
        """
        if parser is None:
            parser = lambda node: (node["name"], (node["x"], node["y"]))
        for node in node_info:
            node_name, pos = parser(node)
            self.vertex_positions[node_name] = pos

    def parse_role(self, node_info: List[Any], parser: Callable[[Any], int] = None):
        """

        :param node_info: A list contains a series of node information.
        :param parser: A Callable to parse the role of vertex.
        :return:
        """
        assert parser is not None
        for node in node_info:
            node_name, colormap = parser(node)
            assert isinstance(colormap, int), "The role of node should be an int."
            self.vertex_roles[node_name] = colormap

    def format(self):
        lst = []
        for name, pos in self.vertex_positions.items():
            lst.append(
                {
                    "name": name,
                    "x": pos[0],
                    "y": pos[1],
                    "category": self.vertex_roles[name],
                }
            )
        lst_edges = []
        for edge, role in self.edge_roles.items():
            lst_edges.append({"source": edge[0], "target": edge[1]})
        data = {
            "visualizer": {"series": [{"data": lst, "links": lst_edges}]},
            "plots": [
                {
                    "chartName": name,
                    "series": [
                        {
                            "name": self.plot_charts[name][i].seriesName,
                            "value": self.chart_data[name][
                                self.plot_charts[name][i].seriesName
                            ][self.current_step],
                        }
                        for i in range(len(self.plot_charts[name]))
                    ],
                }
                for name in self.plot_charts.keys()
            ],
        }
        return data
