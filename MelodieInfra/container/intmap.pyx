import time
from .intmap cimport mld_int_map_create, mld_int_map_free, IntMap, mld_int_map_get, mld_key_in_int_map


cpdef main():
    cdef IntMap* map
    cdef long i = 123
    map = mld_int_map_create(100)
    map.ptr[0] = 123
    t0 = time.time()
    mld_int_map_set(map, 0, i)
    mld_int_map_get(map, 0)
    t1 = time.time()
    print(t1-t0, mld_int_map_get(map, 0))