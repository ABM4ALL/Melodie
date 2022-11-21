# -*- coding:utf-8 -*-
# @Time: 2022/11/21 14:10
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: ws_protocol.py
import http
from typing import Optional

from websockets.datastructures import Headers
from websockets.legacy.server import WebSocketServerProtocol, HTTPResponse


class MelodieVisualizerProtocol(WebSocketServerProtocol):
    async def process_request(
            self, path: str, request_headers: Headers
    ) -> Optional[HTTPResponse]:
        print(path)
        if path != "/":
            return (http.HTTPStatus.OK, [("Access-Control-Allow-Origin", "*")],
                    f"requested at path {path}\n".encode('utf-8', errors='replace'))
        ret = await super().process_request(path, request_headers)
        return ret
