from typing import List, Dict, Any, TYPE_CHECKING, Callable, Tuple, Optional

from Melodie.Element import Element

if TYPE_CHECKING:
    from AgentManager import AgentManager


class Agent(Element):
    def __init__(self, agent_manager: Optional['AgentManager']):
        """
        __init__method contains no parameter.
        """
        self._agent_list: 'AgentManager' = agent_manager
        self.indiced: Dict[Tuple[str], Callable[['Agent'], int]] = {}  # indiced only for numerical property
        self.mapped: Dict[Tuple[str], Callable[['Agent'], int]] = {}  # mapped can be for any computational standards
        self._indiced_watch: Dict[str, Tuple[Tuple[str], List[Callable[['Agent'], int]]]] = {}
        self._mapped_watch: Dict[str, Tuple[Tuple[str], List[Callable[['Agent'], int]]]] = {}

    # readonly property getters
    @property
    def agent_manager(self):
        raise NotImplementedError

    @property
    def scenario(self):
        raise NotImplementedError

    def setup(self):
        pass

    def after_setup(self):
        """
        executed before setup()
        :return:
        """
        for arg_names, func in self.indiced.items():
            if not isinstance(arg_names, tuple):
                raise TypeError('Agent.indiced key type is expected to be Tuple[str,],'
                                f' like (\'aaaaa\',) or (\'bbbbb\',\'aaaa\'). But got type:{type(arg_names)},'
                                f'value: {arg_names}')
            for name in arg_names:
                if name not in self._indiced_watch:
                    self._indiced_watch[name] = (arg_names, [func])
                else:
                    self._indiced_watch[name][1].append(func)

        for arg_names, func in self.mapped.items():
            if not isinstance(arg_names, tuple):
                raise TypeError('Agent.mapped key type is expected to be Tuple[str,],'
                                f' like (\'aaaaa\',) or (\'bbbbb\',\'aaaa\'). But got type:{type(arg_names)},'
                                f'value: {arg_names}')
            for name in arg_names:
                if name not in self._mapped_watch:
                    self._mapped_watch[name] = (arg_names, [func])
                else:
                    self._mapped_watch[name][1].append(func)

    # hook before stepping, stepping and after stepping
    def before_step(self):
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

    def __setattr__(self, name: str, value: Any) -> None:
        """
        设置非索引属性所需时间长9倍
        设置索引属性所需时间长60倍
        """
        if self.__dict__.get('indiced') and name in self._indiced_watch.keys():
            args_tuple, functions = self._indiced_watch[name]
            old_values = [0 * len(functions)]
            for i, fcn in enumerate(functions):
                old_values[i] = fcn(self)
            super().__setattr__(name, value)
            agent_index = self._agent_list.indices[args_tuple]
            for i, fcn in enumerate(functions):
                old_val = old_values[i]
                new_val = fcn(self)
                agent_index.update(self, old_val, new_val)
            return
        elif self.__dict__.get('mapped') and name in self._mapped_watch.keys():
            args_tuple, functions = self._mapped_watch[name]
            old_values = [0 * len(functions)]
            for i, fcn in enumerate(functions):
                old_values[i] = fcn(self)
            super().__setattr__(name, value)
            for i, fcn in enumerate(functions):
                old_val = old_values[i]
                new_val = fcn(self)
                agent_index = self._agent_list.groups[args_tuple]
                agent_index.update(self, old_val, new_val)
            return

        super().__setattr__(name, value)

    def __repr__(self) -> str:

        d = {k: v for k, v in self.__dict__.items() if
             not k.startswith("_")}
        return "<%s %s>" % (self.__class__.__name__, d)
