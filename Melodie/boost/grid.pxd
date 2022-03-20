cdef class Spot:
    cdef public long id
    cdef public long x
    cdef public long y
    cdef public object model, scenario
    cpdef void setup(Spot self)

cdef class Grid:
    cdef long _width
    cdef long _height
    cdef bint wrap
    cdef public dict _existed_agents
    cdef list _spots
    cdef dict _agent_ids
    cdef dict _neighbors_cache
    cpdef add_category(self, object category_name)
    cpdef get_spot(self, long x, long y)
    cpdef get_agent_ids(self, object category, long x, long y)
    cdef long _convert_to_1d(self, long x, long y)
    cdef bint _in_bounds(self, long x, long y)
    cpdef _get_category_of_agents(self, object category_name)
    cdef (long, long) _bound_check(self, long x, long y) except *
    cdef (long, long) _coords_wrap(self, long x ,long y)
    cpdef (long, long) coords_wrap(self, long x, long y)
    cdef list _neighbors(self, long x, long y, long radius, bint moore, bint except_self)
    cdef long _get_neighbors_array_length(self, long radius, bint moore, bint except_self)
    cdef long _get_neighbors_key_hash(self, long x, long y, long radius, bint moore, bint except_self)
    cpdef list get_neighbors(self, long x, long y, long radius=*, bint moore=*, bint except_self=*)
    cpdef long height(self)
    cpdef long width(self)
    cpdef void add_agent(self, long agent_id, object category, long x, long y) except *
    cpdef void remove_agent(self, long agent_id, object category) except *
    cdef void _add_agent(self, long agent_id, object category, long x, long y) except *
    cdef void _remove_agent(self, long agent_id, object category,long x, long y) except *
    cpdef (long, long) get_agent_pos(self, long agent_id, object category)
    cpdef (long, long) rand_move(self, long agent_id, object category, long range_x, long range_y)