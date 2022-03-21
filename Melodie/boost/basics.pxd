from typing import Dict, Any
from typing import Tuple, List, Dict, Optional, TYPE_CHECKING

import pandas as pd

from Melodie.basic import MelodieExceptions

if TYPE_CHECKING:
    from Melodie import Model, Scenario

cdef class Element:
    cpdef void set_params(self, dict params) except *

cdef class Agent(Element):
    cdef public long id
    cdef public object model, scenario


cdef class Environment(Element):
    cdef public object model
    cdef public object scenario
    cpdef void setup(self)

    cpdef dict to_dict(self, list properties)

    cpdef to_dataframe(self, properties: List[str])
