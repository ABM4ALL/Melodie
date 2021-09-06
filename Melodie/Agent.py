from typing import List, Dict, Any, TYPE_CHECKING, Callable, Tuple, Optional, Set, Union

from Melodie.Element import Element
from Melodie.basic import MelodieExceptions

if TYPE_CHECKING:
    from AgentManager import AgentManager

ALLOWED_STATE_TYPES = Union[int, str, tuple]  # A collection of types allowed as state variables
ALLOWED_STATE_TYPES_INSTANCE = (int, str, tuple)


def decorator(transfer: Tuple[ALLOWED_STATE_TYPES, ALLOWED_STATE_TYPES],
              ):
    def outer_wrapper(f):
        def wrapper(agent):
            print(transfer)
            # assert agent
            return f(agent)

        return wrapper

    return outer_wrapper


class Agent(Element):
    def __init__(self, agent_manager: Optional['AgentManager']):
        """
        This method would not be exposed to user.
        """
        self.__dict__['_indiced_watch'] = {}
        self.__dict__['_mapped_watch'] = {}
        self.__dict__['_state_watch'] = {}
        self._agent_list: 'AgentManager' = agent_manager
        self.indiced: Dict[Tuple[str], Callable[['Agent'], int]] = {}  # indiced only for numerical property
        self.mapped: Dict[Tuple[str], Callable[['Agent'], int]] = {}  # mapped can be for any computational standards
        self._indiced_watch: Dict[str, Tuple[Tuple[str], List[Callable[['Agent'], int]]]] = {}
        self._mapped_watch: Dict[str, Tuple[Tuple[str], List[Callable[['Agent'], int]]]] = {}

        self._state_watch: Dict[str, Dict[str, Set[str]]] = {}
        self._state_funcs: Dict[Tuple[ALLOWED_STATE_TYPES, ALLOWED_STATE_TYPES], Callable] = {}

    def __setattr__(self, name: str, value: Any) -> None:
        """
        设置非索引属性所需时间长9倍
        设置索引属性所需时间长60倍
        """
        if name in self._indiced_watch.keys():
            args_tuple, functions = self._indiced_watch[name]
            old_values = [0 * len(functions)]
            for i, fcn in enumerate(functions):
                old_values[i] = fcn(self)
            object.__setattr__(self, name, value)
            agent_index = self._agent_list.indices[args_tuple]
            for i, fcn in enumerate(functions):
                old_val = old_values[i]
                new_val = fcn(self)
                agent_index.update(self, old_val, new_val)
            return
        elif name in self._mapped_watch.keys():
            args_tuple, functions = self._mapped_watch[name]
            old_values = [0 * len(functions)]
            for i, fcn in enumerate(functions):
                old_values[i] = fcn(self)
            object.__setattr__(self, name, value)
            for i, fcn in enumerate(functions):
                old_val = old_values[i]
                new_val = fcn(self)
                agent_index = self._agent_list.groups[args_tuple]
                agent_index.update(self, old_val, new_val)
            return
        elif name in self._state_watch.keys():
            old_value = object.__getattribute__(self, name)
            if value not in self._state_watch[name].keys():
                raise MelodieExceptions.State.StateNotFoundError(value, set(self._state_watch[name].keys()))
            elif value not in self._state_watch[name][old_value]:
                raise MelodieExceptions.State.CannotMoveToNewStateError(old_value, value,
                                                                        set(self._state_watch[name][old_value]))
            else:
                object.__setattr__(self, name, value)
        else:
            object.__setattr__(self, name, value)

    def __repr__(self) -> str:

        d = {k: v for k, v in self.__dict__.items() if
             not k.startswith("_")}
        return "<%s %s>" % (self.__class__.__name__, d)

    # readonly property getters
    @property
    def agent_manager(self):
        raise NotImplementedError

    @property
    def scenario(self):
        raise NotImplementedError

    def add_state_watch(self, attr_name: str, transfer_dict: Dict[ALLOWED_STATE_TYPES, Set[ALLOWED_STATE_TYPES]]):
        if not self.__dict__[attr_name] in transfer_dict.keys():
            raise MelodieExceptions.State.StateNotFoundError(self.__dict__[attr_name], set(transfer_dict.keys()))
        for old_state, new_states in transfer_dict.items():
            assert isinstance(old_state, ALLOWED_STATE_TYPES_INSTANCE)
            for new_state in new_states:
                assert isinstance(new_state, ALLOWED_STATE_TYPES_INSTANCE)
        self._state_watch[attr_name] = transfer_dict

    def setup(self):
        pass

    def after_setup(self):
        """
        executed after setup()
        :return:
        """

    def before_step(self):
        """
        hook before stepping, stepping and after stepping
        :return:
        """
        pass

    def step(self):
        """
        step
        """
        pass

    def after_step(self):
        """
        the hook function called after environment steps
        """
        pass

    def fibonacci(self, n, a=0, b=1):
        if n == 0:  # edge case
            return a
        if n == 1:  # usual base case
            return b
        return self.fibonacci(n - 1, b, a + b)
