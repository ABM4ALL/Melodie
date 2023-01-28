# -*- coding:utf-8 -*-
# @Time: 2022/11/21 14:10
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: ws_protocol.py
import http
import json
import logging
import os.path
from typing import Optional, TYPE_CHECKING
import mimetypes
from urllib.parse import urlparse, parse_qsl

from websockets.datastructures import Headers
from websockets.legacy.server import WebSocketServerProtocol, HTTPResponse

from .actions import Action

if TYPE_CHECKING:
    from .. import Visualizer

logger = logging.getLogger(__name__)


def create_file_response(filepath: str):
    basename, ext = os.path.splitext(filepath)
    mime = mimetypes.types_map[ext]
    logger.info('ext-mime' + f'{mime}')
    with open(filepath, 'rb') as f:
        content = f.read()
    return (http.HTTPStatus.OK, [("Access-Control-Allow-Origin", "*"), ('Content-Type', mime)],
            content)


def create_json_response(obj):
    return http.HTTPStatus.OK, [("Access-Control-Allow-Origin", "*"), ('Content-Type', 'application/json')], \
           json.dumps({"status": 0, "data": obj}).encode('utf8')


def create_failed_response(msg: str):
    return http.HTTPStatus.BAD_REQUEST, [("Access-Control-Allow-Origin", "*")], json.dumps(
        {"status": 1, "msg": msg}).encode('utf8')


class MelodieVisualizerProtocol(WebSocketServerProtocol):
    visualizer: 'Visualizer'

    async def process_request(
            self, path: str, request_headers: Headers
    ) -> Optional[HTTPResponse]:
        """
        Handle requests in visualizer.

        :param path:
        :param request_headers:
        :return:
        """
        try:
            parsed = urlparse(path)
            if path.startswith("/fs/"):
                filepath = path[4:]
                return create_file_response(filepath)
            elif path.startswith("/inspect/"):
                # A dict like  {'a': '123'}
                params = dict(parse_qsl(parsed.query))
                if path.startswith('/inspect/datacollector/timeseries/agent'):
                    agent_id = params.get('id')
                    if agent_id is None:
                        raise ValueError("Agent id does not exist in url")

                    data = self.visualizer.model.data_collector.get_single_agent_data("agents", int(agent_id))
                    return create_json_response(data)
                logger.warning(
                    f'inspect!!! {self.visualizer.model.data_collector.get_single_agent_data("agents", 1)}. {path},')
                raise NotImplementedError
            elif path.startswith("/action/"):
                action = path[len('/action/'):]
                action = action.split("?")[0]
                params = dict(parse_qsl(parsed.query))
                if 'args' in params:
                    args = json.loads(params['args'])
                    args_dict = {arg['name']: arg['value'] for arg in args}
                    logger.warning(f"{params}")
                    return Action.dispatch(action, args_dict)
                else:
                    return Action.dispatch(action)
        except BaseException as e:
            import traceback
            traceback.print_exc()
            return create_failed_response('Request failed: ' + str(e))
        ret = await super().process_request(path, request_headers)
        return ret
