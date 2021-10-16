# -*- coding:utf-8 -*-
# @Time: 2021/10/8 8:26
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: numbaextend.py
from numba import types
from numba.extending import typeof_impl
from numba.extending import type_callable
from numba.extending import box
from numba.extending import unbox, NativeValue

from numba.extending import lower_builtin
from numba.core import cgutils

from numba.extending import overload_attribute

from numba.extending import make_attribute_wrapper
from numba.extending import models, register_model

from Melodie.boost.numbaextend_packed import get_type


class Interval(object):
    """
    A half-open interval on the real number line.
    """
    props = [
        ('lo', types.float64),
        ('hi', types.float64)
    ]

    def __init__(self, lo, hi):
        self.lo = lo
        self.hi = hi

    def __repr__(self):
        return 'Interval(%f, %f)' % (self.lo, self.hi)

    @property
    def width(self):
        return self.hi - self.lo


def wrapper(cls, custom_nb_type: types.Type):
    @typeof_impl.register(cls)
    def typeof_index(val, c):
        return custom_nb_type

    CustomTypeClass = custom_nb_type.__class__

    @register_model(custom_nb_type.__class__)
    class IntervalModel(models.StructModel):
        def __init__(self, dmm, fe_type):
            members = cls.props
            models.StructModel.__init__(self, dmm, fe_type, members)

    for prop in cls.props:
        make_attribute_wrapper(CustomTypeClass, prop[0], prop[0])
        # make_attribute_wrapper(CustomTypeClass, 'hi', 'hi')


IntervalType = get_type('Interval')
interval_type = IntervalType()

wrapper(Interval, interval_type)


# @type_callable(Interval)
# def type_interval(context):
#     def typer(*args):
#         lo, hi = args
#         if isinstance(lo, types.Float) and isinstance(hi, types.Float):
#             return interval_type
#     return typer


# @register_model(IntervalType)
# class IntervalModel(models.StructModel):
#     def __init__(self, dmm, fe_type):
#         members = [
#             ('lo', types.float64),
#             ('hi', types.float64),
#         ]
#         models.StructModel.__init__(self, dmm, fe_type, members)


# make_attribute_wrapper(IntervalType, 'lo', 'lo')
# make_attribute_wrapper(IntervalType, 'hi', 'hi')


@overload_attribute(IntervalType, "width")
def get_width(interval):
    def getter(interval):
        return interval.hi - interval.lo

    return getter


@lower_builtin(Interval, types.Float, types.Float)
def impl_interval(context, builder, sig, args):
    typ = sig.return_type
    lo, hi = args
    interval = cgutils.create_struct_proxy(typ)(context, builder)
    interval.lo = lo
    interval.hi = hi
    return interval._getvalue()


@unbox(IntervalType)
def unbox_interval(typ, obj, c):
    """
    Convert a Interval object to a native interval structure.
    """
    lo_obj = c.pyapi.object_getattr_string(obj, "lo")
    hi_obj = c.pyapi.object_getattr_string(obj, "hi")
    interval = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    interval.lo = c.pyapi.float_as_double(lo_obj)
    interval.hi = c.pyapi.float_as_double(hi_obj)
    c.pyapi.decref(lo_obj)
    c.pyapi.decref(hi_obj)
    is_error = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(interval._getvalue(), is_error=is_error)


@box(IntervalType)
def box_interval(typ, val, c):
    """
    Convert a native interval structure to an Interval object.
    """
    interval = cgutils.create_struct_proxy(typ)(c.context, c.builder, value=val)
    lo_obj = c.pyapi.float_from_double(interval.lo)
    hi_obj = c.pyapi.float_from_double(interval.hi)
    class_obj = c.pyapi.unserialize(c.pyapi.serialize_object(Interval))
    res = c.pyapi.call_function_objargs(class_obj, (lo_obj, hi_obj))
    c.pyapi.decref(lo_obj)
    c.pyapi.decref(hi_obj)
    c.pyapi.decref(class_obj)
    return res


################################################
from numba import jit


@jit(nopython=True)
def inside_interval(interval, x):
    return interval.lo <= x < interval.hi


@jit(nopython=True)
def interval_width(interval):
    return interval.width


@jit(nopython=True)
def sum_intervals(i, j):
    for t in range(1000000):
        i[0].lo + j.lo, i[0].hi + j.hi


class PlainInterval(object):

    def __init__(self, lo, hi):
        self.lo = lo
        self.hi = hi

    def __repr__(self):
        return 'Interval(%f, %f)' % (self.lo, self.hi)

    @property
    def width(self):
        return self.hi - self.lo


def sum2(i, j):
    for k in range(1000000):
        i.lo + j.lo, i.hi + j.hi


N = 10
import timeit

r = timeit.timeit('sum_intervals((Interval(1, 1),), Interval(2, 2))',
                  number=N, globals=globals())
print(r)
r = timeit.timeit('sum2(PlainInterval(1, 1), PlainInterval(2, 2))',
                  number=N, globals=globals())
print(r)
# print(sum_intervals(Interval(1, 1), Interval(2, 2)))
