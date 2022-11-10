# -*- coding:utf-8 -*-
# @Time: 2022/11/9 10:41
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: params.py.py
import math
from typing import Callable, Any, TYPE_CHECKING, Tuple, Union, List, Dict

from Melodie.visualizer import JSONBase

if TYPE_CHECKING:
    from Melodie import Scenario

GetterType = 'Callable[[object], Any]'
SetterType = 'Callable[[object, Param], Any]'
GetterArgType = Union[GetterType, str]
SetterArgType = Union[SetterType, str]

BasicType = Union[str, int, float, bool]
ParamsType = 'Union[Param, IntParam, FloatParam, BoolParam, StringParam, ArrayParam]'


class UnInitialized:
    pass


class Param(JSONBase):
    def validate_getter_or_setter(self, f):
        assert isinstance(f, str) or callable(f), 'Argument `getter` and `setter` should be callable or string'

    def __init__(self, name: str, getter: GetterArgType, setter: SetterArgType, readonly=False, label="",
                 component='auto'):
        self.name = name
        self.label = label
        self.type = ''
        self.component: str = component
        if isinstance(getter, str) and getter == '':
            getter = name
        if isinstance(setter, str) and setter == '':
            setter = name
        self.validate_getter_or_setter(getter)
        self.validate_getter_or_setter(setter)
        self._value: Any = UnInitialized()
        self.readonly = readonly

        self._getter_from_obj: GetterType = getter if callable(getter) else \
            lambda obj: getattr(obj, getter)
        self._setter_to_obj: SetterType = setter if callable(setter) else \
            lambda obj, param: setattr(obj, setter, param.value)

    @property
    def value(self):
        return self._value

    def children(self):
        return None

    @value.setter
    def value(self, new_val):
        new_val = self._converter(new_val)
        self._validator(new_val)
        assert isinstance(new_val, type(self._value)) or isinstance(self._value, UnInitialized), (
            'new value', type(new_val), 'old value', type(self._value), 'does not match')
        self._value = new_val

    def to_json(self):
        d = super().to_json()
        return d

    def to_value_json(self):
        return {'value': self._value, 'type': self.type, 'name': self.name}

    def _validator(self, new_val):
        return

    def _converter(self, new_val):
        return new_val

    def extract_value(self, obj: "object"):
        self.value = self._getter_from_obj(obj)

    def modify_object(self, obj: 'object'):
        """
        Modify property inside the obj.

        :param obj:
        :return:
        """
        self._setter_to_obj(obj, self)


class IntParam(Param):
    """
    Integer parameter.

    Notice:

    The parameter `value_range` indicates a **closed** interval.

    For example, if `value_range` is a tuple `(0, 100)`, both 0 and 100 are valid values.

    Be sure to check the right boundary in case of out-of-range error when you are using this value as indices.

    """
    _value: int

    def __init__(self, name: str, value_range: Tuple[int, int], getter: GetterArgType = "", setter: SetterArgType = "",
                 readonly=False, label="",
                 component='auto', ):
        super().__init__(name, getter, setter, readonly, label, component)

        self.min = value_range[0]
        self.max = value_range[1]
        self.type = 'int'

    def _validator(self, new_val: int):
        if not self.min <= new_val <= self.max:
            raise ValueError(f"Integer value {new_val} out of range {self.min}<= x <={self.max}")

    def _converter(self, new_val):
        return int(new_val)


class BoolParam(Param):
    """
    Boolean parameter

    """
    _value: bool

    def __init__(self, name: str, getter: GetterArgType = "", setter: SetterArgType = "",
                 readonly=False, label="",
                 component='auto', ):
        super().__init__(name, getter, setter, readonly, label, component)
        self.type = 'bool'


class StringParam(Param):
    """
    String parameter
    
    """
    _value: bool

    def __init__(self, name: str, getter: GetterArgType = "", setter: SetterArgType = "",
                 readonly=False, label="",
                 component='auto', ):
        super().__init__(name, getter, setter, readonly, label, component)
        self.type = 'str'


class FloatParam(Param):
    """
    Parameter with float value.

    precision: An integer for float digit numbers, -1 by default, indicating no rounding.
    """
    _value: float

    def __init__(self, name: str, value_range: Tuple[float, float], step: float = -1,
                 getter: GetterArgType = "",
                 setter: SetterArgType = "",
                 readonly=False, label="",
                 component='auto', ):
        super().__init__(name, getter, setter, readonly, label, component)

        self.min = value_range[0]
        self.max = value_range[1]
        self.step = step
        self.type = 'float'

    def _validator(self, new_val: int):
        if not self.min - 10 ** -9 <= new_val <= self.max + 10 ** -9:
            raise ValueError(f"Float parameter named {self.name}, value {new_val} out of range {self.min}<= x <={self.max}")

    # def _converter(self, new_val):
    #     if self.precision < 0:
    #         return new_val
    #     return round(new_val, self.precision)


class ArrayParam(Param):
    """
    Parameters could be set inside an array

    """
    _value: "List[Union[IntParam, FloatParam, ArrayParam]]"

    def __init__(self, name: str, value: "List[Union[IntParam, FloatParam, ArrayParam]]", getter: GetterArgType = '',
                 setter: SetterArgType = '', readonly=False, label="", component='auto'):
        super().__init__(name, getter, setter, readonly, label, component)
        self._value = value
        self.type = 'array'
        for val in self._value:
            assert isinstance(val, (IntParam, FloatParam, ArrayParam, BoolParam, StringParam))

    def children(self):
        return self._value

    @property
    def value(self):
        return [param.value for param in self._value]

    @value.setter
    def value(self, new_val: List[BasicType]):

        assert len(new_val) == len(self._value)
        for i, val in enumerate(self._value):
            val.value = new_val[i]

    def to_json(self):
        items = []
        for param in self._value:
            items.append(param.to_json())
        d = super().to_json()
        d['children'] = items
        return d
        # return {"type": 'array', "name": self.name, "children": items}

    def to_value_json(self):
        return {"type": 'array', "name": self.name, "value": [param.to_value_json() for param in self._value]}

    def extract_value(self, obj: "object"):
        # subobj = self._getter_from_obj(obj)
        for param in self._value:
            # subobj = param._getter_from_obj(obj)
            param.extract_value(obj)


class ParamsManager:
    def __init__(self):
        self._unique_name_map: Dict[str, Param] = {}
        self.params: List[ParamsType] = []

    def add_param(self, param: ParamsType):
        self.params.append(param)

    # def load_scenario(self, scenario: 'Scenario'):
    # for param
    def to_json(self):
        return [param.to_json() for param in self.params]

    @staticmethod
    def write_obj_attrs_to_params_list(obj: object, params: List[ParamsType]):
        for param in params:
            param.extract_value(obj)

    @staticmethod
    def for_each_param(params: List[ParamsType], name_prefix: str, callback: Callable[[str, Param], None]):
        """
        Walk through the parameter tree to gather each parameter value into a plain list.

        :param params:
        :param name_prefix:
        :param callback:
        :return:
        """
        for param in params:
            assert isinstance(param, Param), param
            abs_name = name_prefix + "." + param.name
            if isinstance(param, ArrayParam):
                ParamsManager.for_each_param(param.children(), abs_name, callback)
            else:
                callback(abs_name, param)

    def to_form_model(self):
        new_params_list = []

        # def for_each_callback(param_name: str, param: Param):
        #     d = param.to_json()
        #     d['name'] = param_name
        #     new_params_list.append(d)
        #
        # ParamsManager.for_each_param(self.params, "", for_each_callback)
        return [param.to_json() for param in self.params]

    def to_value_json(self):
        new_params_list = []

        # def for_each_callback(param_name: str, param: Param):
        #     d = param.to_value_json()
        #     d['name'] = param_name
        #     new_params_list.append(d)
        #
        # ParamsManager.for_each_param(self.params, "", for_each_callback)
        return [param.to_value_json() for param in self.params]
