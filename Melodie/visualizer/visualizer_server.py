import base64
import json
import logging
import queue
import threading

from flask import Flask, Response, abort, request
from flask_cors import CORS
from flask_sock import Sock, Server, ConnectionClosed as WSClosed
from typing import List, Set

from .actions import ToolbarAction

logger = logging.getLogger(__name__)


def create_visualizer_server(recv_queue: queue.Queue, send_queue: queue.Queue, port: int):
    app = Flask(__name__)
    sock = Sock(app)
    websockets: List[Server] = []

    CORS(app, supports_credentials=True)

    def send():
        while 1:
            try:
                data = send_queue.get(timeout=1)
                closed_websockets: Set[int] = set()
                for websocket in websockets:
                    try:
                        websocket.send(data)
                    except WSClosed:
                        closed_websockets.add(id(websocket))
                        pass
                for ws_index in range(len(websockets) - 1, 0, -1):
                    if id(websockets[ws_index]) in closed_websockets:
                        websockets.pop(ws_index)
            except queue.Empty:
                pass

    thread_send = threading.Thread(target=send)
    thread_send.setDaemon(True)
    thread_send.start()

    @app.route("/visualizer/action/<string:action_name>")
    def handle_action(action_name: str):
        if 'args' in request.args:
            logger.warning(f"args: {request.args}")
            args = json.loads(base64.b64decode(request.args['args']))
            args_dict = {arg['name']: arg['value'] for arg in args}
            logger.warning(f"{args}")
            ret, stat = ToolbarAction.dispatch(action_name, args_dict)
        else:
            ret, stat = ToolbarAction.dispatch(action_name)
        if not stat:
            abort(Response(ret, status=400))
            return ""
        return ret

    @app.route('/visualizer/action-params/<string:action_name>')
    def handle_action_params(action_name: str):
        resp = {"status": 0, "data": ToolbarAction.get_custom_args(action_name)}
        return json.dumps(resp)

    @sock.route('/visualizer/echo')
    def echo(ws: Server):
        from .visualizer import HEARTBEAT, WSMsgType
        websockets.append(ws)
        while True:
            try:
                content = ws.receive()
                # if content.startswith()
                rec = json.loads(content)
                cmd = rec["cmd"]
                data = rec["data"]
                if cmd == HEARTBEAT:
                    continue
                if 0 <= cmd < 100:
                    try:
                        recv_queue.put((cmd, data), timeout=1)
                    except:
                        import traceback
                        traceback.print_exc()
                else:
                    raise NotImplementedError(cmd)
            except json.JSONDecodeError:
                import traceback
                traceback.print_exc()

    app.run(host='0.0.0.0', port=port)
