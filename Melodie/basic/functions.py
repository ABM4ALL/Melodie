import dis
from typing import List, Callable
import logging

logger = logging.getLogger(__name__)


def parse_watched_attrs(func) -> List[str]:
    """
    Parse watched attributes from a function instance.
    This function works on the bytecode of input function to get all attributes should be watched.

    Notice:
    1. The result of this function may not be always accurate. It's suggested to assign watched
       attribute names to function manually.
    2. The attribute to be watched are expected to be immutable objects(int, float, str, tuple).
       If not, the index may not be updated properly.
    :param func: A single-positional-argument function like `def func(a):a+1`
    :return: A List[str] contains
    """
    bytecode = dis.Bytecode(func)

    IDLE = 0
    ARG_VAR_LOADED = 1
    status = IDLE
    if func.__code__.co_argcount != 1:
        raise ValueError('The query %s should have only one argument' % func)
    argname = func.__code__.co_varnames[0]
    attr_watch_list: List[str] = []

    for instr in bytecode:
        print(instr.opname, instr.argval)
        if instr.opname == 'LOAD_FAST':
            if instr.argval == argname:
                status = ARG_VAR_LOADED
            else:
                status = IDLE
        elif instr.opname == 'LOAD_ATTR':
            if status == ARG_VAR_LOADED:
                attr_watch_list.append(instr.argval)
                status = IDLE
        else:
            status = IDLE

    return attr_watch_list


if __name__ == "__main__":
    def f():
        return True


    def f1(agent, fwer):
        a = 123
        b = 456
        if a == b:
            c = 45
            pass


    print(f1.__code__.co_varnames, f1.__code__.co_argcount)


    class A:
        def f(self):
            pass

        def a(self):
            # a = 0
            # b = 0
            # c =
            a = {}
            b = dict()
            return
            # return ((self.name + self.app) is ({}.get(''))) or (self.app.started == True)


    s = parse_watched_attrs(A().a)
    print(s)
    print(dis.dis(A().a))
