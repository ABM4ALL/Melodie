import base64
import logging
import os
import json
import queue
import shutil
import threading
import time
from enum import Enum

from typing import Dict, Tuple, List, Any, Callable, Union, TYPE_CHECKING, Optional
from MelodieInfra import OSTroubleShooter, get_sqlite_filename, MelodieExceptions, Config

from .actions import ToolbarAction
from .visualizer_server import create_visualizer_server
from MelodieInfra.lowcode.params import ParamsManager
from .vis_agent_series import AgentSeriesManager
from .vis_charts import ChartManager
from ..boost.grid import Spot

if TYPE_CHECKING:
    from Melodie import Scenario, Model, Grid, Network, Agent, AgentList, Simulator

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
SAVE_PARAMS = 7
SAVE_DATABASE = 8
DOWNLOAD_DATA = 9
GENERAL_COMMAND = 10
HEARTBEAT=100

UNCONFIGURED = 0
READY = 1
RUNNING = 2
FINISHED = 3

# Response status code
OK = 0
ERROR = 1


class WSMsgType(str, Enum):
    INIT_OPTION = 'initOption'
    INIT_PLOT_SERIES = "initPlotSeries"
    NOTIFICATION = "notification"
    PARAMS = "params"
    SIMULATION_DATA = "data"
    ACTIONS = "actions"
    FILE = "file"
    HEARTBEAT = "heartbeat"


class MelodieModelReset(BaseException):
    def __init__(self, ws=None):
        self.ws = ws


def execute_only_enabled(func):
    """
    Execute the decorated function only if the Visualizer.enabled() is True.
    :param func:
    :return:
    """

    def wrapper(*args, **kwargs):
        if BaseVisualizer.enabled:
            return func(*args, **kwargs)

    return wrapper


class BaseVisualizer:
    enabled = True  # If in the Simulator.run() or Simulator.run_parallel(), this flag will be set to False

    def __init__(self, config: Config, simulator: "Simulator"):
        self.config = config
        self.simulator = simulator
        self.current_step = 0
        self.model_state = UNCONFIGURED
        self.current_scenario: "Scenario" = None
        self.actions: List[ToolbarAction] = []

        self.params_dir = os.path.join(config.visualizer_tmpdir, 'params')
        self.sim_data_dir = os.path.join(config.visualizer_tmpdir, 'sim_data')
        if not os.path.exists(self.params_dir):
            os.makedirs(self.params_dir)
        if not os.path.exists(self.sim_data_dir):
            os.makedirs(self.sim_data_dir)

        self._model: "Model" = None
        self.params_manager: ParamsManager = ParamsManager()
        self.scenario_param: Dict[str, Union[int, str, float]] = {}
        self.visualizer_components: List[
            Tuple["Callable[[],ComponentType]", str, str, Dict, Dict, Callable[["Agent"], int]]
        ] = []

        self.plot_charts: ChartManager = ChartManager()
        self.agent_series_managers: Dict[str, AgentSeriesManager] = {}
        self.agent_lists: Dict[int, "AgentList"] = {}

        self.th: Optional[threading.Thread] = None
        self.send_queue = queue.Queue()
        self.recv_queue = queue.Queue()

        try:
            self.start_websocket()
        except OSError as err:
            OSTroubleShooter().handle_exc(err)
            raise err

    @execute_only_enabled
    def start_websocket(self):
        server_logger = logging.getLogger('websocket-server')
        server_logger.setLevel(logging.ERROR)
        host = "localhost"

        self.th = threading.Thread(target=create_visualizer_server,
                                   args=(self.recv_queue, self.send_queue, self.config.visualizer_port))

        self.th.setDaemon(True)
        self.th.start()

        logger.info("\n" + "=" * 100 + f"\nVisualizer started at {host}:{self.config.visualizer_port}\n" + "=" * 100)

    def add_action(self, action: ToolbarAction):
        self.actions.append(action)

    def setup(self):
        pass

    def reset(self):
        pass

    def _format(self):
        pass

    @property
    def model(self):
        return self._model

    def _re_init(self):
        """
        Re-init the status of visualizer.
        :return:
        """
        self.agent_series_managers = {}
        self.plot_charts = self.plot_charts
        self.scenario_param = {}

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

    def send_actions(self):
        data = [action.to_json() for action in self.actions]
        self.send_msg(WSMsgType.ACTIONS, 0, data)

    def put_message(self, msg: str):
        """
        Put message to the message queues of all active websocket connections.
        If the target queue is full, the message will be discarded.
        :param msg:
        :return:
        """
        self.send_queue.put(msg)

    def send_msg(self, msg_type: WSMsgType, period: int, data: Any, status: int = OK):
        """
        Format input arguments to json and send the json.
        :param msg_type:
        :param period:
        :param data:
        :param status:
        :return:
        """
        return self.put_message(
            json.dumps(
                {
                    "type": msg_type,
                    "period": period,
                    "data": data,
                    "modelState": self.model_state,
                    "status": status,
                }
            )
        )

    def get_visualizers_initial_options(self):
        initial_options = []
        for (
                component,
                component_name,
                component_type,
                options,
                roles,
                var_getter,
        ) in self.visualizer_components:
            if component_type == "grid":

                initial_options.append(self.parse_grid_series(component(), roles, var_getter, True))
            else:
                initial_options.append(self.parse_network_series(component(), roles, var_getter))
        return initial_options

    def send_chart_options(self):
        self.send_msg(WSMsgType.INIT_OPTION, 0, self.get_visualizers_initial_options())

    def send_notification(self, message: str, type: str = 'info', title="Notice"):
        assert type in {'success', 'info', 'warning', 'error'}
        self.send_msg(WSMsgType.NOTIFICATION, 0, {"type": type, "title": title, "message": message})

    def send_plot_series(self):
        self.send_msg(WSMsgType.INIT_PLOT_SERIES, 0, self.plot_charts.to_json())

    def send_scenario_params(self, params_set_name: str):
        all_param_names = [os.path.splitext(filename)[0] for filename in
                           os.listdir(self.params_dir)]
        if params_set_name in all_param_names:
            with open(os.path.join(self.params_dir, params_set_name + '.json'), encoding='utf8', errors='replace') as f:
                params_json = json.load(f)
                self.params_manager.from_json(params_json)
                self.send_notification(f"Parameters updated to param set {params_set_name}")

        params = {"initialParams": self.params_manager.to_value_json(),
                  "paramModels": self.params_manager.to_form_model(),
                  "allParamSetNames": all_param_names}
        self.send_msg(WSMsgType.PARAMS, self.current_step, params)

    def send_current_data(self):
        t0 = time.time()
        formatted = self._format()
        t1 = time.time()
        logger.info(f"Formatting current data takes:{t1 - t0} seconds")
        self.send_msg(WSMsgType.SIMULATION_DATA, self.current_step, formatted)

    def send_error(self, err_msg):
        self.send_msg(WSMsgType.SIMULATION_DATA, self.current_step, err_msg, ERROR)

    def get_in_queue(self) -> Tuple[int, Dict[str, Any]]:
        """
        `while 1` statement was for checking the sigterm signal.

        :return:
        """
        while 1:
            try:
                res = self.recv_queue.get(timeout=1)
                handled = self.generic_handler(*res)
                assert isinstance(handled, bool)
                if not handled:
                    return res
                else:
                    pass
            except queue.Empty:
                pass

    def generic_handler(
            self, cmd_type: int, data: Dict[str, Any]
    ) -> bool:
        """
        The handler for viewing current data, getting scenario parameters.

        :param cmd_type:
        :param data:
        :param ws:
        :return:
        """
        if cmd_type == GET_PARAMS:
            self.send_scenario_params(data.get('name'))
            return True
        elif cmd_type == RESET:
            try:
                self.params_manager.from_json(data['params'])
                raise MelodieModelReset
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.send_notification("Parameter value error:" + str(e), "error")
                return True
        elif cmd_type == INIT_OPTIONS:
            self.send_chart_options()
            self.send_plot_series()
            self.send_actions()
            return True
        elif cmd_type == SAVE_PARAMS:
            file = os.path.join(self.params_dir, f"{data['name']}.json")
            with open(file, 'w', encoding='utf-8', errors='replace') as f:
                json.dump(data['params'], f, indent=4, ensure_ascii=False)
            self.send_notification("Parameters saved successfully", "success")
            return True
        elif cmd_type == SAVE_DATABASE:

            exported_file = os.path.join(self.sim_data_dir, f"{data['name']}.sqlite")
            shutil.copy(get_sqlite_filename(self.config), exported_file)
            self.send_notification("Database saved successfully!", "success")
            return True
        elif cmd_type == DOWNLOAD_DATA:
            sqlite_file = get_sqlite_filename(self.config)
            if os.path.exists(sqlite_file):
                with open(sqlite_file, 'rb') as f:
                    self.send_msg(WSMsgType.FILE, self.current_step, {"name": data['name'] + '.sqlite',
                                                                      "content":
                                                                          base64.b64encode(f.read()).decode('ascii')},
                                  ERROR)

                self.send_notification("Database exported successfully!", "success")
            else:
                self.send_notification("Database exported error: No database file found!", "error")
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
            flag, data = self.get_in_queue()
            if flag in {STEP, CURRENT_DATA}:
                self.send_current_data()
                if (
                        flag == STEP
                ):  # If the flag was period, then go to period No.1. So there should be one
                    # queue to put into the condition queue.
                    self.model_state = RUNNING
                    self.recv_queue.put((flag, {}))
                    break
            else:
                self.send_error(f"Invalid command flag {flag} for function 'start'. ")

    def step(self, current_step):
        self.model_state = RUNNING
        self.current_step = current_step
        self.plot_charts.update(self.current_step)
        while 1:
            logger.info("in period")
            flag, data = self.get_in_queue()
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
            flag, data = self.get_in_queue()
            if flag == CURRENT_DATA:
                self.send_current_data()
            else:
                if flag == STEP:
                    self.send_error(f"Model already finished, please reset the model.")
                else:
                    self.send_error(
                        f"Invalid command flag {flag} for function 'finish'. "
                    )


class Visualizer(BaseVisualizer):
    """
    The visualizer
    """

    def __init__(self, config: Config, simulator):
        super().__init__(config, simulator)
        self.height = 0
        self.width = 0
        self.spots_status_change = True
        self.grid_roles = []

        self.grid_params = {}

    def reset(self):
        self.grid_roles = []
        self.grid_params = {}
        self.plot_charts.reset()

    def convert_to_1d(self, x, y):
        return x * self.height + y

    def parse_grid_series(self, grid: "Grid", styles, var_getter, initialize=False):

        agents_vis_dicts = []
        spots = []

        spot_attributes = ["id", "x", "y"] + list(grid.get_spot(0, 0).__dict__.keys())
        if self.spots_status_change or initialize:
            if isinstance(grid.get_spot(0, 0), Spot):
                for x in range(grid.width()):
                    for y in range(grid.height()):
                        spot = grid.get_spot(x, y)
                        spots.append(
                            {
                                "data": spot.to_dict(spot_attributes),
                                "style": spot.get_style(),
                            }
                        )
        for agent_category in grid.get_agent_categories:
            agent_list = grid.get_agent_container(agent_category)
            if len(agent_list) == 0:
                continue
            first_agent = agent_list[0]
            attributes = ["id", "x", "y", "category"] + list(
                first_agent.__dict__.keys()
            )
            for agent in agent_list:
                agents_vis_dicts.append(
                    {"data": agent.to_dict(attributes), "style": styles[var_getter(agent)]}
                )
        return {
            "name": "grid",
            "type": "grid",
            "agents": agents_vis_dicts,
            "spots": spots,
        }

    def parse_network_series(self, network: 'Network', roles, var_getter: 'Callable[[Agent], int]'):
        data = []
        # network.agent_categories
        for category, agent_id in network.nodes:
            agent = network.agent_categories[category].get_agent(agent_id)
            layout = network.get_position(agent.category, agent.id)
            data.append(
                {"name": f"{agent.category}-{agent.id}", "agentCategory": category,
                 "category": var_getter(agent),
                 "x": layout[0],
                 "y": layout[1]
                 })
        links = []
        for start_node in network.edges.keys():
            for end_node in network.edges[start_node]:
                links.append(
                    {
                        "source": f'{start_node[0]}-{start_node[1]}',
                        "target": f'{end_node[0]}-{end_node[1]}',
                    },
                )
        categories = [{
                          "name": roles[i]['label'],
                          "itemStyle": {
                              "color": roles[i]['color'],
                          },
                      } if i in roles else {} for i in range(min(roles.keys()), max(roles.keys()) + 1)]
        legends = [{"data": [roles[i]['label'] if i in roles else "" for i in
                             range(min(roles.keys()), max(roles.keys()) + 1)]}]
        d = {
            "legend": legends,
            "series": [
                {
                    "type": "graph",
                    "layout": "none",
                    "symbolSize": 5,
                    "symbol": "circle",

                    "roam": True,
                    "itemStyle": {
                        "opacity": 1
                    },
                    "scaleLimit": [0.1, 100],
                    "edgeSymbol": ["circle", "arrow"],
                    "edgeSymbolSize": [4, 5],
                    "categories": categories,
                    "data": data,
                    "links": links
                },
            ],
        }
        return {
            "name": "network",
            "type": "network",
            "graph": d
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

    def add_network(self, name: str, network_getter: "Callable[[], ComponentType]",
                    var_style: Dict[int, Dict] = None,
                    var_getter: Callable[["Agent"], int] = None):
        """
        Add a network onto the visualizer.
        :param name:
        :param network_getter:
        :param var_style:
        :param var_getter:
        :return:
        """

        self.visualizer_components.append(
            (network_getter, name, 'network', {}, var_style, var_getter)
        )

    def add_grid(
            self,
            name: str,
            grid_getter: "Callable[[], ComponentType]",
            var_style: Dict[int, Dict] = None,
            var_getter: Callable[["Agent"], int] = None,
            update_spots=True
    ):
        """
        Add a Grid onto the visualizer.

        :param name: The name of grid component.
        :param grid_getter: The getter function returning a Grid object.
        :param var_style:  The style of different agent categories.
        :param var_getter: The getter of agent variable.
        :param update_spots:  This argument is True by default, indicating rendering all spots in each step.
            If False, spots will not be rendered during simulation.
        :return:
        """
        self.spots_status_change = update_spots

        self.visualizer_components.append(
            (grid_getter, name, "grid", {}, var_style, var_getter)
        )

    def _format(self):
        visualizers = []
        for (
                vis_component,
                vis_component_name,
                vis_component_type,
                _1,
                roles,
                var_getter,
        ) in self.visualizer_components:
            if vis_component_type == 'grid':
                r = self.parse_grid_series(vis_component(), roles, var_getter)
                visualizers.append(r)
            elif vis_component_type == 'network':

                visualizers.append(self.parse_network_series(vis_component(), roles, var_getter))
            else:
                raise NotImplementedError
        data = {
            "visualizers": visualizers,
            "plots": self.plot_charts.get_current_data(),
        }

        return data
