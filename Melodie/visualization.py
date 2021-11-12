import logging
import asyncio
import queue
import threading
import time

import websockets
import json
from queue import Queue
from typing import Dict, Tuple, List, Any, Callable, Union
from signal import SIGINT, SIGTERM
from websockets.legacy.server import WebSocketServerProtocol

from Melodie import Scenario
from Melodie.grid import Grid, Spot

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

STEP = 0
RESET = 1
CURRENT_DATA = 2
START = 3
GET_PARAMS = 4
SET_PARAMS = 5

UNCONFIGURED = 0
READY = 1
RUNNING = 2
FINISHED = 3

# Response status code
OK = 0
ERROR = 1

QUEUE_ELEM = Tuple[int, WebSocketServerProtocol]

visualize_condition_queue_main = Queue(1)

socks: List[WebSocketServerProtocol] = list()


def on_close():
    print("closed!")
    pass


# 一旦websocket 改变，则应当测试已有的ws。如果已有的ws出现问题，则应该？？？
# 如果连接已经下线，则？


async def handler(websocket: WebSocketServerProtocol, path):
    global socks
    new_socks = []
    for sock in socks:
        if not sock.closed:
            new_socks.append(sock)
        print(sock.closed)
    print("this-ws", websocket.closed)
    socks = new_socks
    socks.append(websocket)
    while 1:
        content = await websocket.recv()
        rec = json.loads(content)
        cmd = rec['cmd']
        data = rec['data']
        if 0 <= cmd <= 5:
            visualize_condition_queue_main.put((cmd, data, websocket))
        else:
            raise NotImplementedError(cmd)


async def send_message(sock: WebSocketServerProtocol, msg):
    await sock.send(msg)


class MelodieModelReset(BaseException):
    def __init__(self, ws: WebSocketServerProtocol = None):
        self.ws = ws


class Visualizer():
    def __init__(self):
        self.current_step = 0
        self.model_state = UNCONFIGURED
        self.current_scenario: 'Scenario' = None
        self.scenario_param: Dict[str, Union[int, str, float]] = {}

        self.current_websocket: WebSocketServerProtocol = None

        start_server = websockets.serve(handler, 'localhost', 8765)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio_serve = asyncio.get_event_loop().run_forever
        self.th = threading.Thread(target=asyncio_serve)

        self.th.setDaemon(True)
        self.th.start()

    def reset(self):
        pass

    def format(self):
        pass

    def send_initial_msg(self, ws: WebSocketServerProtocol):
        formatted = self.format()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_message(ws, json.dumps(formatted)))
        loop.close()

    async def _send_message(self, msg: str):
        assert self.current_websocket is not None
        if self.current_websocket.closed:
            logger.fatal("Current websocket was closed!")
            return
        else:
            await self.current_websocket.send(msg)

    def send_message(self, msg):
        # asyncio.run(self._send_message(msg))
        # asyncio.get_event_loop()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            self._send_message(msg))
        loop.close()

    def send_scenario_params(self, params_list: List[Scenario.BaseParameter]):
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
        print(json.dumps(
            {"type": "params", "step": self.current_step, "data": params, "modelState": self.model_state, "status": OK},
            indent=4))

    def send_current_data(self):
        formatted = self.format()
        # try:
        self.send_message(
            json.dumps(
                {"type": "data", "step": self.current_step, "data": formatted, "modelState": self.model_state,
                 "status": OK}))
        # except:
        #     import traceback
        #     traceback.print_exc()

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
            flag, data, ws = self.get_in_queue()
            if flag in {STEP, CURRENT_DATA}:
                self.send_current_data()
                if flag == STEP:  # If the flag was step, then go to step No.1. So there should be one
                    # queue to put into the condition queue.
                    self.model_state = RUNNING
                    visualize_condition_queue_main.put((flag, {}, ws))
                    break
            elif flag == RESET:
                raise MelodieModelReset
            else:
                self.send_error(f"Invalid command flag {flag} for function 'start'. ")

    def step(self, current_step=-1):
        self.model_state = RUNNING
        if current_step >= 0:
            self.current_step = current_step
        else:
            self.current_step += 1
        while 1:
            flag, data, ws = self.get_in_queue()
            if flag == STEP:
                self.send_current_data()
                break
            elif flag == CURRENT_DATA:
                self.send_current_data()
            elif flag == RESET:
                raise MelodieModelReset
            else:
                self.send_error(f"Invalid command flag {flag} for function 'step'. ")

    def finish(self):
        self.model_state = FINISHED
        self.send_current_data()
        while 1:
            flag, data, ws = self.get_in_queue()
            if flag == RESET:
                raise MelodieModelReset(ws)
            elif flag == CURRENT_DATA:
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

    def reset(self):
        self.grid_roles = []
        self.grid_params = {}

    def convert_to_1d(self, x, y):
        return x * self.height + y

    def parse_grid_roles(self, grid: Grid, parser: Callable[['Spot'], int]):
        self.width = grid.width
        self.height = grid.height
        self.grid_roles = [None for i in range(grid.height * grid.width)]
        if isinstance(grid, Grid):
            for x in range(grid.width):
                for y in range(grid.height):
                    spot = grid.get_spot(x, y)
                    role = parser(spot)
                    if role < 0:
                        self.grid_roles[self.convert_to_1d(x, y)] = [x, y, "-", 0]
                    else:
                        self.grid_roles[self.convert_to_1d(x, y)] = [x, y, 1, role]
        else:
            raise NotImplementedError

    def format(self):
        data = {
            "series": {
                "data": self.grid_roles,
            }
        }
        return data


class NetworkVisualizer(Visualizer):
    def __init__(self):
        super().__init__()

        logger.info("Network visualizer server is starting...")

        self.vertex_positions: Dict[str, Tuple[int, int]] = {}
        self.vertex_roles: Dict[str, int] = {}
        self.edge_roles: Dict[Tuple[int, int], int] = {}

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
            "series": {
                "data": lst,
                "links": lst_edges
            }
        }
        return data
