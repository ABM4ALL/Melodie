JIT_AVAILABLE = False
try:

    from .grid import JITGrid
    from .network import JITNetwork

    JIT_AVAILABLE = True
except:
    import traceback

    traceback.print_exc()
