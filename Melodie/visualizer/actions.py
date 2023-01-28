# -*- coding:utf-8 -*-
# @Time: 2022/12/8 22:47
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: actions.py
from typing import Callable, Dict, List, Optional
from MelodieInfra.jsonobject import JsonObject, StringProperty, ObjectProperty
from .params import ParamsManager
from .vis_charts import JSONBase


class BasicOprandType(JSONBase):
    def __init__(self):
        self.type = ''

    def __eq__(self, other):
        assert isinstance(other, BasicOprandType)
        return other.type == self.type


class JSONOprandType(BasicOprandType):
    def __init__(self):
        self.type = 'json'


class FileOprandType(BasicOprandType):
    """
    File Oprand.
    In JS, it is a `File()` Object.

    """

    def __init__(self):
        self.type = 'file'


class ResponseOprandType(BasicOprandType):
    """
    Response oprand.
    In JS, it is an axios response.

    """

    def __init__(self):
        self.type = 'response'


class Operation(JSONBase):

    def __init__(self, oprands: Optional[List['Operation']]):
        self.name = ""
        self.oprands: List[Operation] = oprands if oprands is not None else []
        assert isinstance(self.oprands, list)
        self.optypes = []
        self.rettype = None
        self.type = None

    def check_type(self):
        assert len(self.oprands) == len(self.optypes), (self.optypes, self.oprands)
        for oprand, optype in zip(self.oprands, self.optypes):
            assert oprand.rettype == optype, (oprand.rettype, optype)


class ResponseConversionOperation(Operation):
    pass


class ResponseToFile(ResponseConversionOperation):
    names_map = {"default_name": "defaultName"}

    def __init__(self, default_name: str, oprands: Optional[List['Operation']] = None):
        super().__init__(oprands)
        self.name = 'op-response-to-file'
        self.default_name = default_name
        self.optypes = []
        self.rettype = FileOprandType()


class ResponseToJSON(ResponseConversionOperation):

    def __init__(self, oprands: Optional[List['Operation']] = None):
        super().__init__(oprands)
        self.name = 'op-response-to-json'
        self.rettype = JSONOprandType()


class DownloadOperation(Operation):

    def __init__(self, oprands: Optional[List['Operation']] = None):
        super().__init__(oprands)
        self.name = "op-download"
        self.optypes = [FileOprandType()]
        self.rettype = None
        print(self.oprands)


class ShowChartWindowOperation(Operation):
    def __init__(self, oprands: Optional[List['Operation']] = None):
        super().__init__(oprands)
        self.name = "op-show-chart-window"
        self.optypes = [JSONOprandType()]
        self.rettype = None
        print(self.oprands)


class Action(JSONBase):
    handlers_map = {}

    def __init__(self, key: str, text: str, operation: Operation, handler: Callable,
                 custom_args: Optional[ParamsManager] = None):
        self.key = key
        self.text = text
        self.operation = operation
        self.operation.check_type()
        self._handler = handler
        self.children = []
        self.custom_args = custom_args.to_json() if isinstance(custom_args, ParamsManager) else []
        Action.handlers_map[key] = handler

    def add_sub_action(self, action: "Action"):
        self.children.append(action)

    @classmethod
    def dispatch(cls, key, args: Dict = None):
        if args is None:
            args = {}
        return cls.handlers_map[key](**args)
