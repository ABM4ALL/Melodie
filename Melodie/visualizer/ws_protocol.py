# -*- coding:utf-8 -*-
# @Time: 2022/11/21 14:10
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: ws_protocol.py
import http
import logging
import os.path
from typing import Optional
import mimetypes
from websockets.datastructures import Headers
from websockets.legacy.server import WebSocketServerProtocol, HTTPResponse

from .actions import Action

logger = logging.getLogger(__name__)


def create_file_response(filepath: str):
    basename, ext = os.path.splitext(filepath)
    mime = mimetypes.types_map[ext]
    logger.info('ext-mime' + f'{mime}')
    with open(filepath, 'rb') as f:
        content = f.read()
    return (http.HTTPStatus.OK, [("Access-Control-Allow-Origin", "*"), ('Content-Type', mime)],
            content)


def create_failed_response(msg: str):
    return http.HTTPStatus.BAD_REQUEST, [("Access-Control-Allow-Origin", "*")], msg.encode('utf8')


class MelodieVisualizerProtocol(WebSocketServerProtocol):
    async def process_request(
            self, path: str, request_headers: Headers
    ) -> Optional[HTTPResponse]:
        """
        Handle requests in visualizer.

        :param path:
        :param request_headers:
        :return:
        """
        if path.startswith("/fs/"):
            filepath = path[4:]
            return create_file_response(filepath)
        elif path.startswith("/action/"):
            action = path[len('/action/'):]
            return Action.dispatch(action)
        ret = await super().process_request(path, request_headers)
        return ret
