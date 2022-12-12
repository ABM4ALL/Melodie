# Boost Python with vectorization

It is a well-known issue that pythoner always get speed penalties when enjoying speedy development. Melodie, based on
python, was no exception.

## Introduction

### Why Python Slow

- Interpretation. Comparing to C/C++, C#, Golang, Python is slower than them because it runs with a interpreter, not
  Native Code.

- Lack of JIT. Comparing to Javascript, another famous interpretative language, the interpreter of Python lacks
  Just-In-Time compilation.

- Dynamic Type. Comparing to Java, Python does not have a static type system for checking and optimization.

### Common ways to improve performance

- Cython.
    - As python has great affinity for C binding, cython was introduced for writing python-like code to generate C code.
      Well-compiled cython code runs as fast as C.
    - However, writting cython code and bind python objects to it may not be a easy task.
- Numba.
    - Numba was a python JIT compiler based on LLVM, compiling python code to native code at runtime. If JIT warms up,
      it will run as fast as C.
    - Numba needs some time to warm up. If the script is executed only once, the just-in-time compilation can be
      useless.
    - Numba does not support Object-Oriented Programming in python.
- PyPy
    - PyPy is a brand-new interpreter with a Just-In-Time compiler. Developers need not change any code, just download
      this interpreter and then enjoy 3~10 times speed up.
    - However, PyPy was not good at calling python-c interface. Manipulating numpy arrays or pandas dataframe could be
      annoying slow——even many times slower than CPython!

### Optimizations for ABM Frameworks

For Agent-Based Modelling Frameworks, on the one hand, they are Object-Oriented program, which makes it hard for
adopting Cython or Numba for speed up. But on the other hand, we must use numpy, pandas and many other C-bound tools for
data exploration, which are the weakness of PyPy interpreter.

TO speed up, Mesa, another ABM framework, avoided using Python-C APIs(and third-party packages such as numpy, pandas) to
ensure PyPy could do its best. But in contrary, Melodie decided to optimize the performance of CPython interpreter as
much as possible.

## Vectorization in Melodie

### Principle

Melodie uses cython to accelerate property access. At the cython layer, Melodie will gather property of all agents,
returning a numpy array.

Once we have got the array, we could use broadcast manipulations to speed up. Furthermore, to gain a extreme speed
increase, we could use numba in a independent function.

Notice that when you changed item value in the array, the corresponding property of the agent will **not** be changed.
In order to gain better performance, we should call `broadcast` methods to apply the change.

```python
from Melodie.boost import broadcast_2d, gather_2d


class PurePyCell():
    def __init__(self) -> None:
        self.x = 0
        self.y = 0
        self.a = 1
        self.b = 0.1


XM = 100
YM = 100

pure_py_lst = [[PurePyCell() for i in range(XM)] for j in range(YM)]

res = gather_2d(pure_py_lst, 'b')
res += 1
broadcast_2d(pure_py_lst, 'b', res)
```

### A demo of Game of Life

Think of a "Game of Life". If you are not familiar with it,
hit [here](http://pi.math.cornell.edu/~lipa/mec/lesson6.html)

All cells are on a grid, the simple rules are as follows:

- If the cell is alive, then it stays alive if it has either 2 or 3 live neighbors
- If the cell is dead, then it springs to life only in the case that it has 3 live neighbors

```python

```

(Not accomplished)



