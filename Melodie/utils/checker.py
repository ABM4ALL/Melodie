import logging
from typing import Callable

from MelodieInfra.exceptions.exceptions import MelodieExceptions

logger = logging.getLogger(__name__)


def args_check(func: Callable, expected_arg_num: int):
    if func.__code__.co_argcount != expected_arg_num:
        raise MelodieExceptions.Program.Function.FunctionArgsNumError(
            func, expected_arg_num, func.__code__.co_argcount
        )
