# cython:language_level=3
from .basics cimport Agent
from .agent_list cimport AgentList
cimport numpy as np
from libcpp.vector cimport vector
from libcpp.unordered_set cimport unordered_set as cpp_set
from libcpp.map cimport map as cpp_map
from libcpp.string cimport string as cpp_string

cdef class GridItem(Agent):
    cdef public long x
    cdef public long y
    cdef public Grid grid
    cpdef void set_params(self, dict params) except *

cdef class GridAgent(GridItem):
    cdef public long category
    cpdef rand_move_agent(self, int x_range, int y_range) except *

cdef class Spot(GridItem):
    cdef public long colormap

cdef class AgentIDManager:
    cdef long _width
    cdef long _height
    cdef vector[cpp_set[long]] _agents
    cdef long _max_id
    cdef cpp_set[long] _empty_spots
    cdef bint allow_multi
    cdef public cpp_set[long] all_categories 
    cdef void _add_agent(self, long agent_id, long category, long x, long y) except *
    cpdef add_agent(self, long agent_id, long category, long x, long y) except *
    cdef void _remove_agent(self, long agent_id, long category, long x, long y) except *
    cpdef remove_agent(self, long agent_id, long category, long x, long y) except *

    cdef long _convert_to_1d(self, long x, long y)
    
    cdef cpp_set[long]* _get_empty_spots(self)

    cpdef set get_empty_spots(self)
    cpdef long agent_id_and_category_to_number(self, long agent_id, long category) except *
    cdef (long, long) num_to_2d_coor(self, long num) except *
    cpdef (long, long) number_to_category_and_agent_id(self, long num) except *

    cpdef list agents_on_spot(self, long x, long y) except *
    cdef (long, long) find_empty_spot(self) except *

cdef class Grid:
    cdef long _width
    cdef long _height
    cdef bint _multi
    cdef bint _caching
    cdef bint _wrap
    cdef public dict _existed_agents
    cdef list _spots
    cdef dict _agent_ids
    cdef dict _neighbors_cache
    cdef list _roles_list
    cdef list _agent_containers
    cdef set _agent_categories
    cdef public object scenario
    cdef public object _spot_cls
    
    cdef AgentIDManager _agent_id_mgr
    cpdef _add_agent_container(self, object category , str initial_placement) except *
    cpdef AgentList get_agent_container(self, category_id) except *
    cpdef Spot get_spot(self, long x, long y)
    cdef long _convert_to_1d(self, long x, long y)
    cdef bint _in_bounds(self, long x, long y)
    cpdef list _get_agent_id_set_list(self, object category_name)
    cdef (long, long) _bound_check(self, long x, long y) except *
    cdef (long, long) _coords_wrap(self, long x ,long y)
    cpdef (long, long) coords_wrap(self, long x, long y)

    cdef list _neighbors(self, long x, long y, long radius, bint moore, bint except_self)
    cdef long _get_neighbors_array_length(self, long radius, bint moore, bint except_self)
    cdef long _get_neighbors_key_hash(self, long x, long y, long radius, bint moore, bint except_self)
    cpdef list _get_neighbor_positions(self, long x, long y, long radius=*, bint moore=*, bint except_self=*)
    

    cpdef long height(self)
    cpdef long width(self)
    
    cpdef void add_agent(self, GridAgent agent) except *
    cpdef void remove_agent(self, GridAgent agent) except *
    cpdef void move_agent(self, GridAgent agent, long target_x, long target_y) except *
    cpdef list get_spot_agents(self, Spot spot) except *
    cdef void _add_agent(self, long agent_id, long category, long x, long y) except *
    cdef void _remove_agent(self, long agent_id, long category,long x, long y) except *
    cpdef list get_neighbors(self, GridAgent agent, long radius=*, bint moore=*, bint except_self=*) except *
    
    cpdef (long, long) rand_move_agent(self, GridAgent agent, long category, long range_x, long range_y) except *
    cpdef tuple get_colormap(self)
    cpdef (long, long) find_empty_spot(self) except *
    cpdef list get_empty_spots(self) except *