from numba import float64
from numba.experimental import jitclass


@jitclass([
    ("a", float64),
    ("c", float64[:])
])
class A:
    def __init__(self) -> None:
        self.a = 123.8
    def a123(self):
        self.b = self.a

spec1 = [
    ("a", float64),
    ("c", float64[:])
]
@jitclass(spec1)
class A2:
    def __init__(self) -> None:
        self.a = 123.8
    def a123(self):
        self.b = self.a
