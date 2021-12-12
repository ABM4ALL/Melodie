import json
import logging
from os import error, stat
from typing import Any

logger = logging.getLogger(__file__)


class Response:
    OK = 0
    ERROR = 1

    @staticmethod
    def _create_response(status: int, message: str, data: Any) -> str:
        assert status in {Response.OK, Response.ERROR}
        try:
            resp = json.dumps({"status": status,
                               "msg": message,
                               "data": data})
        except TypeError:
            import traceback
            traceback.print_exc()
            logger.error(str(data))
            # return
        if status == Response.ERROR:
            logger.info(resp)
        return resp

    @staticmethod
    def ok(data: Any) -> str:
        return Response._create_response(Response.OK, "", data)

    @staticmethod
    def error(msg: str) -> str:
        return Response._create_response(Response.ERROR, msg, None)
