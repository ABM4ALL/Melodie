# -*- coding:utf-8 -*-
# @Time: 2022/11/9 10:41
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: params.py.py
import math
from typing import Callable, Any, TYPE_CHECKING, Tuple, Union, List, Dict

from .vis_charts import JSONBase

if TYPE_CHECKING:
    from Melodie import Scenario

GetterType = 'Callable[[object], Any]'
SetterType = 'Callable[[object, Param], Any]'
GetterArgType = Union[GetterType, str]
SetterArgType = Union[SetterType, str]

BasicType = Union[str, int, float, bool]
ParamsType = 'Union[Param, IntParam, FloatParam, BoolParam, StringParam, ArrayParam]'


class UnInitialized:
    """
    Special class standing for uninitialized variable

    """
    pass


class Param(JSONBase):
    """
    Basic Parameter object

    """

    def validate_getter_or_setter(self, f):
        assert isinstance(f, str) or callable(f), 'Argument `getter` and `setter` should be callable or string'

    def __init__(self, name: str, getter: GetterArgType, setter: SetterArgType, readonly=False, label="",
                 description="No description about this parameter...",
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
        self.description = description

        self._getter_from_obj: GetterType = getter if callable(getter) else \
            lambda obj: getattr(obj, getter)
        self._setter_to_obj: SetterType = setter if callable(setter) else \
            lambda obj, param: setattr(obj, setter, param)

    @property
    def value(self):
        """
        Get Value

        :return:
        """
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
        """
        Convert param structure to json

        :return:
        """
        d = super().to_json()
        return d

    def to_value_json(self):
        """
        Convert param value to json

        :return:
        """
        return {'value': self._value, 'type': self.type, 'name': self.name}

    def _validator(self, new_val):
        return

    def _converter(self, new_val):
        """
        Convert any valid value to integer.

        :param new_val:
        :return:
        """
        return new_val

    def extract_value(self, obj: "object"):
        """
        Get value from object with getter

        :param obj:
        :return:
        """
        self.value = self._getter_from_obj(obj)

    def modify_object(self, obj: 'object'):
        """
        Modify property inside the object with setter.

        :param obj:
        :return:
        """
        self._setter_to_obj(obj, self.value)

    def from_json(self, d: Dict):
        """
        Load this object from json-dumpable(parsable) dict object

        :param d:
        :return:
        """
        self.value = d['value']


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
                 description="",
                 component='auto', ):
        super().__init__(name, getter, setter, readonly, label, description, component)

        self.min = value_range[0]
        self.max = value_range[1]
        self.type = 'int'

    def _validator(self, new_val: int):
        """
        Int value should be in range

        :param new_val:
        :return:
        """
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
                 description="",
                 component='auto', ):
        super().__init__(name, getter, setter, readonly, label, description, component)
        self.type = 'bool'

    def _converter(self, new_val):
        return bool(new_val)


class StringParam(Param):
    """
    String parameter
    
    """
    _value: bool

    def __init__(self, name: str, getter: GetterArgType = "", setter: SetterArgType = "",
                 readonly=False, label="",
                 description="",
                 component='auto', ):
        super().__init__(name, getter, setter, readonly, label, description, component)
        self.type = 'str'

    def _converter(self, new_val):
        return str(new_val)


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
                 description="",
                 component='auto', ):
        super().__init__(name, getter, setter, readonly, label, description, component)

        self.min = value_range[0]
        self.max = value_range[1]
        self.step = step
        self.type = 'float'

    def _validator(self, new_val: int):
        if not self.min - 10 ** -9 <= new_val <= self.max + 10 ** -9:
            raise ValueError(
                f"Float parameter named {self.name}, value {new_val} out of range {self.min}<= x <={self.max}")

    def _converter(self, new_val):
        return float(new_val)


class ArrayParam(Param):
    """
    Parameters could be set inside an array

    """
    _value: "List[Union[IntParam, FloatParam, ArrayParam]]"

    def __init__(self, name: str, value: "List[Union[IntParam, FloatParam, ArrayParam]]", getter: GetterArgType = '',
                 setter: SetterArgType = '', readonly=False, label="", description="", component='auto'):
        super().__init__(name, getter, setter, readonly, label, description,
                         component)
        self._value = value
        self.type = 'array'
        for val in self._value:
            assert isinstance(val, (IntParam, FloatParam, ArrayParam, BoolParam, StringParam))

    def children(self):
        """
        Get the parameters in the array.

        :return:
        """
        return self._value

    @property
    def value(self):
        """
        Getter of value, a list.

        :return:
        """
        return [param.value for param in self._value]

    @value.setter
    def value(self, new_val: List[BasicType]):
        """
        Setter of value

        :param new_val:
        :return:
        """
        assert len(new_val) == len(self._value)
        for i, val in enumerate(self._value):
            val.value = new_val[i]

    def to_json(self):
        """
        Convert to json

        :return:
        """
        items = []
        for param in self._value:
            items.append(param.to_json())
        d = super().to_json()
        d['children'] = items
        return d

    def to_value_json(self):
        """
        Convert to value json.

        :return:
        """
        return {"type": 'array', "name": self.name, "value": [param.to_value_json() for param in self._value]}

    def extract_value(self, obj: "object"):
        """
        Extract value from each child

        :param obj:
        :return:
        """
        for param in self._value:
            param.extract_value(obj)

    def from_json(self, d: List[Union[List, Dict]]):
        """
        Set value of each child from a json-dumpable list

        :param d:
        :return:
        """
        assert isinstance(d['value'], list)
        assert len(d['value']) == len(self._value)
        for i, param in enumerate(self._value):
            param.from_json(d['value'][i])

    def modify_object(self, obj: 'object'):
        """
        Modify each child with theirs setter

        :param obj:
        :return:
        """
        for param in self._value:
            param.modify_object(obj)


class ParamsManager:
    """
    Manager of parameters

    The parameter settings panel will be shown top-down on the left side of simulator page, and all parameter object
    added by `add_param` method will be put in a top-down layout.

    """

    def __init__(self):
        self._initialized = False
        self._unique_name_map: Dict[str, Param] = {}
        self.params: List[ParamsType] = []

    def add_param(self, param: ParamsType):
        """
        Add a parameter onto the panel.

        :param param:
        :return:
        """
        self.params.append(param)

    def to_json(self):
        """
        Convert the contained parameters to json

        :return:
        """
        return [param.to_json() for param in self.params]

    def modify_scenario(self, scenario: 'Scenario'):
        """
        Write parameter values to scenario object

        :param scenario:
        :return:
        """
        for param in self.params:
            param.modify_object(scenario)

    @staticmethod
    def write_obj_attrs_to_params_list(obj: object, params: List[ParamsType]):
        """
        Extract property value of object to parameters.

        :param obj:
        :param params:
        :return:
        """
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
        """
        Convert data model to a json-dumpable list.

        :return:
        """
        return [param.to_json() for param in self.params]

    def to_value_json(self):
        """
        Convert value model to a json-dumpable list.

        :return:
        """
        return [param.to_value_json() for param in self.params]

    def from_json(self, l: List[Union[Dict, List]]):
        """
        Extract value of parameters from a json-dumpable list

        :param l:
        :return:
        """
        assert len(l) == len(self.params)
        for i, param in enumerate(self.params):
            param.from_json(l[i])
