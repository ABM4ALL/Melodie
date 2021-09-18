from typing import Dict, Tuple, Set, List, Callable, Union

ALLOWED_STATE_TYPES = Union[int, str, tuple]  # A collection of types allowed as state variables
ALLOWED_STATE_TYPES_INSTANCE = (int, str, tuple)

TRANSITION_TYPE = Tuple[ALLOWED_STATE_TYPES, ALLOWED_STATE_TYPES]


class StatesManager:
    def __init__(self):
        self._state_funcs: Dict[str, Dict[Tuple[ALLOWED_STATE_TYPES, ALLOWED_STATE_TYPES], Callable]] = {}
        self._state_watch: Dict[str, Dict[str, Set[str]]] = {}
        self._state_trigger_attrs: Dict[str, List[Callable]] = {}  # {'attr': [lambda agent:agent.attr==1,]}

    def add_transition_func(self, state_attr: str, transition: TRANSITION_TYPE, condition: Callable[]):
        if state_attr not in self._state_funcs.keys():
            self._state_funcs[state_attr] = {}
        self._state_funcs[state_attr][transition] = condition

        if state_attr not in self._state_watch.keys():
            self._state_watch[state_attr] = {}
        if transition[0] not in self._state_watch[state_attr].keys():
            self._state_watch[state_attr][transition[0]] = set()
        if transition[1] not in self._state_watch[state_attr].keys():
            self._state_watch[state_attr][transition[1]] = set()

        self._state_watch[state_attr][transition[0]].add(transition[1])
