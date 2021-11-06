import logging
import asyncio
import threading
import time

import websockets
import json
from queue import Queue
from typing import Dict, Tuple, List, Any, Callable, Union

from websockets.legacy.server import WebSocketServerProtocol

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

STEP = 0
RESET = 1
CURRENT_DATA = 2
START = 3

UNCONFIGURED = 0
READY = 1
RUNNING = 2
FINISHED = 3

# Response status code
OK = 0
ERROR = 1

QUEUE_ELEM = Tuple[int, WebSocketServerProtocol]

visualize_condition_queue_main = Queue(1)
# visualize_condition_queue_server = Queue(1)

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
        if content == "STEP":
            visualize_condition_queue_main.put((STEP, websocket))
        elif content == "RESET":
            visualize_condition_queue_main.put((RESET, websocket))
        elif content == "START":
            visualize_condition_queue_main.put((START, websocket))
        elif content == "CURRENT_DATA":
            visualize_condition_queue_main.put((CURRENT_DATA, websocket))
        else:
            raise NotImplementedError(content)


async def send_message(sock: WebSocketServerProtocol, msg):
    await sock.send(msg)


start_server = websockets.serve(handler, 'localhost', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio_serve = asyncio.get_event_loop().run_forever


class MelodieModelReset(BaseException):
    def __init__(self, ws: WebSocketServerProtocol = None):
        self.ws = ws


class NetworkVisualizer():
    def __init__(self):
        self.current_step = 0
        self.model_state = UNCONFIGURED

        self.current_websocket: WebSocketServerProtocol = None

        self.th = threading.Thread(target=asyncio_serve)
        self.th.setDaemon(True)
        self.th.start()

        logger.info("Network visualizer server is starting...")
        self.vertex_positions: Dict[str, Tuple[int, int]] = {}
        self.vertex_roles: Dict[str, int] = {}

        self.edge_roles: Dict[Tuple[int, int], int] = {}
        self.scenario_param: Dict[str, Union[int, str, float]] = {}

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
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            self._send_message(msg))
        loop.close()

    def send_current_data(self):
        formatted = self.format()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            self._send_message(
                json.dumps(
                    {"step": self.current_step, "data": formatted, "modelState": self.model_state, "status": OK})))
        loop.close()

    def send_error(self, err_msg):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            self._send_message(
                json.dumps({"step": self.current_step, "data": err_msg, "modelState": 10, "status": ERROR})))
        loop.close()

    def start(self):
        self.model_state = READY
        self.current_step = 0
        try:
            self.send_current_data()
        except:
            import traceback
            traceback.print_exc()

        while 1:
            flag, ws = visualize_condition_queue_main.get()
            self.current_websocket = ws
            if flag in {START, CURRENT_DATA}:
                self.send_current_data()
                if flag == START:
                    self.model_state = RUNNING
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
            flag, ws = visualize_condition_queue_main.get()
            self.current_websocket = ws
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
            flag, ws = visualize_condition_queue_main.get()
            self.current_websocket = ws
            if flag == RESET:
                raise MelodieModelReset(ws)
            elif flag == CURRENT_DATA:
                self.send_current_data()
            else:
                self.send_error(f"Invalid command flag {flag} for function 'finish'. ")
