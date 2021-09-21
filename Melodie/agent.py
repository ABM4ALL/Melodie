import functools
import os
from typing import List, Dict, Any, TYPE_CHECKING, Callable, Tuple, Optional, Set, Union

from Melodie.element import Element
from Melodie.basic import MelodieExceptions, parse_watched_attrs

if TYPE_CHECKING:
    from .agent_manager import AgentManager

ALLOWED_STATE_TYPES = Union[int, str, tuple]  # A collection of types allowed as state variables
ALLOWED_STATE_TYPES_INSTANCE = (int, str, tuple)


class Agent(Element):
    def __init__(self, agent_id: int):
        self.id = agent_id
        pass

    def setup(self):
        pass

    def __repr__(self) -> str:
        d = {k: v for k, v in self.__dict__.items() if
             not k.startswith("_")}
        return "<%s %s>" % (self.__class__.__name__, d)


class StateAgent(Agent):
    _state_funcs: Dict[str, Dict[Tuple[ALLOWED_STATE_TYPES, ALLOWED_STATE_TYPES], Callable]] = {}
    _state_watch: Dict[str, Dict[str, Set[str]]] = {}
    _state_trigger_attrs: Dict[str, List[Callable]] = {}  # {'attr': [lambda agent:agent.attr==1,]}

    def __init__(self, agent_manager: Optional['AgentManager']):
        """
        This method would not be exposed to user.
        """
        self.__dict__['_indiced_watch'] = {}
        self.__dict__['_mapped_watch'] = {}
        self._agent_list: 'AgentManager' = agent_manager
        self.indiced: Dict[Tuple[str], Callable[['Agent'], int]] = {}  # indiced only for numerical property
        self.mapped: Dict[Tuple[str], Callable[['Agent'], int]] = {}  # mapped can be for any computational standards
        self._indiced_watch: Dict[str, Tuple[Tuple[str], List[Callable[['Agent'], int]]]] = {}
        self._mapped_watch: Dict[str, Tuple[Tuple[str], List[Callable[['Agent'], int]]]] = {}

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
            if name not in self.__dict__.keys():
                object.__setattr__(self, name, value)
                if value not in self._state_watch[name].keys():
                    raise MelodieExceptions.State.StateNotFoundError(value, set(self._state_watch[name].keys()))
                return
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

        # if name in self._state_trigger_attrs.keys():
        #     for f in self._state_trigger_attrs[name]:
        #         f(self)

    # readonly property getters
    @property
    def agent_manager(self):
        raise NotImplementedError

    @property
    def scenario(self):
        raise NotImplementedError

    # @classmethod
    # def add_state_watch(cls, attr_name: str, transfer_dict: Dict[ALLOWED_STATE_TYPES, Set[ALLOWED_STATE_TYPES]]):
    #     if not self.__dict__[attr_name] in transfer_dict.keys():
    #         raise MelodieExceptions.State.StateNotFoundError(self.__dict__[attr_name], set(transfer_dict.keys()))
    #     for old_state, new_states in transfer_dict.items():
    #         assert isinstance(old_state, ALLOWED_STATE_TYPES_INSTANCE)
    #         for new_state in new_states:
    #             assert isinstance(new_state, ALLOWED_STATE_TYPES_INSTANCE)
    #     self._state_watch[attr_name] = transfer_dict

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

    def current_state_is(self, state_attr: str, cmp_state: str) -> bool:
        """
        Get if self.<state_attr> == cmp_state
        if `cmp_state` is not defined or cannot transfer to `cmp_state`, raise error
        if `state_attr` is not a state attribute, raise error
        :param state_attr:
        :param cmp_state:
        :return:
        """
        if state_attr not in self._state_watch.keys():
            raise MelodieExceptions.State.NotAStateAttributeError(self.__class__, state_attr)
        if cmp_state not in self._state_watch[state_attr].keys():
            raise MelodieExceptions.State.StateNotFoundError(cmp_state, set(self._state_watch.keys()))
        return self.__dict__[state_attr] == cmp_state

    #
    # @functools.lru_cache
    # def get_state_funcs(self, arguments):
    #     return self._state_funcs['status']

    @classmethod
    def state_transition(cls, watched_attr: str, transition: Tuple[ALLOWED_STATE_TYPES, ALLOWED_STATE_TYPES],
                         ):
        if watched_attr not in cls._state_funcs.keys():
            cls._state_funcs[watched_attr] = {}
        if watched_attr not in cls._state_watch.keys():
            cls._state_watch[watched_attr] = {}

        if transition not in cls._state_funcs[watched_attr].keys():
            cls._state_funcs[watched_attr][transition] = {}

        if transition[0] not in cls._state_watch[watched_attr].keys():
            cls._state_watch[watched_attr][transition[0]] = set()
        if transition[1] not in cls._state_watch[watched_attr].keys():
            cls._state_watch[watched_attr][transition[1]] = set()

        cls._state_watch[watched_attr][transition[0]].add(transition[1])

        def outer_wrapper(f):

            cls._state_funcs[watched_attr][transition] = f

            def wrapper(agent):  # 调用层
                res = f(agent)
                # if not isinstance(res, bool):
                #     return
                # else:
                #     if res:
                #         agent.__setattr__(watched_attr, transition[1])
                return res

            attrs = parse_watched_attrs(f)
            for attr in attrs:
                if attr not in cls._state_trigger_attrs.keys():
                    cls._state_trigger_attrs[attr] = []

                cls._state_trigger_attrs[attr].append(wrapper)

            return wrapper

        return outer_wrapper

    def plot_md(self):
        graph_str = 'graph TD\n'
        watch = self._state_watch['status']
        funcs = self._state_funcs['status']
        for old_state, new_states in watch.items():
            for new_state in new_states:
                func = funcs[(old_state, new_state)]
                print(func.__qualname__)
                func_name = ".".join(func.__qualname__.rsplit('.', maxsplit=2)[-2:])
                graph_str += f'{old_state}-->|{func_name}|{new_state}\n'
        with open(r'C:\Users\12957\Documents\Developing\Python\melodie\Melodie\static\mermaid.html', 'r') as f:
            html = f.read()
            html = html.replace('TEMPLATE', graph_str)
            with open('out.html', 'w') as f:
                f.write(html)
                os.startfile('out.html')
