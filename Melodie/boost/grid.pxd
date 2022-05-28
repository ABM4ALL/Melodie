# cython:language_level=3
from .basics cimport Agent
from .agent_list cimport AgentList
cimport numpy as np
from libcpp.vector cimport vector
from libcpp.set cimport set as cpp_set
from libcpp.map cimport map as cpp_map
from libcpp.string cimport string as cpp_string

cdef class GridItem(Agent):
    cdef public long x
    cdef public long y
    cpdef void set_params(self, dict params) except *

cdef class GridAgent(GridItem):
    cdef public long category

cdef class Spot(GridItem):
    cdef public long role

cdef class AgentIDManager:
    cdef long _width
    cdef long _height
    cdef vector[cpp_set[long]] _agents
    cdef long _max_id
    cdef cpp_set[long] _empty_spots
    cdef bint allow_multi
    cdef public cpp_set[long] all_categories 
    cpdef add_agent(self, long agent_id, long category, long x, long y) except *
    
    cpdef remove_agent(self, long agent_id, long category, long x, long y) except *

    cdef long _convert_to_1d(self, long x, long y)
    
    cdef cpp_set[long]* _get_empty_spots(self)

    cpdef set get_empty_spots(self)
    cpdef long agent_id_and_category_to_number(self, long agent_id, long category) except *
    cdef (long, long) num_to_2d_coor(self, long num) except *
    cpdef (long, long) number_to_agent_id_and_category(self, long num) except *

    cpdef list agents_on_spot(self, long x, long y) except *
    cdef (long, long) find_empty_spot(self) except *

cdef class Grid:
    cdef long _width
    cdef long _height
    cdef bint _multi
    cdef bint wrap
    cdef public dict _existed_agents
    cdef list _spots
    cdef dict _agent_ids
    cdef dict _neighbors_cache
    cdef list _roles_list
    cdef list _agent_containers
    
    cdef AgentIDManager _agent_id_mgr
    cpdef  validate(self)
    cpdef _add_agent_container(self, long category_id, AgentList category , str initial_placement) except *
    cdef AgentList get_agent_container(self, category_id) except *
    cpdef get_spot(self, long x, long y)
    # cpdef get_agent_ids(self, object category, long x, long y)
    cdef long _convert_to_1d(self, long x, long y)
    cdef bint _in_bounds(self, long x, long y)
    cpdef list _get_agent_id_set_list(self, object category_name)
    cdef (long, long) _bound_check(self, long x, long y) except *
    cdef (long, long) _coords_wrap(self, long x ,long y)
    cpdef (long, long) coords_wrap(self, long x, long y)
    cdef list _neighbors(self, long x, long y, long radius, bint moore, bint except_self)
    cdef long _get_neighbors_array_length(self, long radius, bint moore, bint except_self)
    cdef long _get_neighbors_key_hash(self, long x, long y, long radius, bint moore, bint except_self)
    cpdef list get_neighbors(self, long x, long y, long radius=*, bint moore=*, bint except_self=*)
    cpdef long height(self)
    cpdef long width(self)
    cpdef void add_agent(self, GridAgent agent, long category) except *
    cpdef void remove_agent(self, GridAgent agent, long category) except *
    cpdef void move_agent(self, GridAgent agent, long category, long target_x, long target_y) except *
    cpdef list get_agents(self, long x, long y) except *
    cpdef list get_agent_ids(self, long x, long y) except *
    cdef void _add_agent(self, long agent_id, long category, long x, long y) except *
    cdef void _remove_agent(self, long agent_id, long category,long x, long y) except *
    # cpdef (long, long) get_agent_pos(self, long agent_id, object category)
    cpdef (long, long) rand_move(self, GridAgent agent, long category, long range_x, long range_y) except *
    cpdef tuple get_roles(self)
    cpdef (long, long) find_empty_spot(self) except *