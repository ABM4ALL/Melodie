JIT_AVAILABLE = False
try:

    from .grid import JITGrid
    from .network import JITNetwork

    JIT_AVAILABLE = True
except:
    import traceback

    traceback.print_exc()

def fake_jit(*args, **kwargs):
    """
    A fake jit if numba is not available
    :param args:
    :param kwargs:
    :return:
    """

    def deco_func(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return deco_func
