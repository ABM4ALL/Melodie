# cython:language_level=3
# distutils: language = c++
import time
from libc.stdint cimport uintptr_t
from libcpp.vector cimport vector
from libcpp.set cimport set as cpp_set
from libcpp.map cimport map as cpp_map
from libcpp.string cimport string as cpp_string

cdef list test():
    cdef vector[int] v = [4, 6, 5, 10, 3]
    cdef cpp_set[int] s = {0, 1, 2,3 }
    cdef int value
    v.push_back(0)
    for value in v:
        print(value)
    print("========"*5)
    s.insert(4)
    for value in s:
        print(value)
    s.erase(0)
    print("========"*5)
    for value in s:
        print(value)
    return [x*x for x in v if x % 2 == 0]

cdef speed_benchmark():
    N = 1000
    
    cdef dict d = {0: 0}
    cdef set s = {0}
    cdef cpp_set[int] s2 = {0}
    cdef int a
    cdef cpp_map[int, vector[cpp_set[int]]] manager = {0: [{1,2,3}]}
    cdef cpp_map[int, vector[int]] manager_ptr = {0: [0]}
    
    t0 = time.time()
    for i in range(N):
        d[0]

    t1 = time.time()
    for i in range(N):
        manager[0][0].insert(0)

    t2 = time.time()
    for i in range(N):
        print(<uintptr_t>&manager[0][0])

    t3 = time.time()
    print(t1-t0, t2-t1, t3-t2)


cdef test2():
    cdef cpp_map[cpp_string, int] manager = {bytes("aaa",'utf8'): 0}
    cdef vector[cpp_set[int]] v = []
    cdef cpp_set[int] _set = {0, 1, 2, 3}
    # v = [_set]
    v.push_back(_set)
    manager[b'bbbb'] = 1
    print(v)
    print(manager)
    

def main():
    test()
    # test2()
    speed_benchmark()