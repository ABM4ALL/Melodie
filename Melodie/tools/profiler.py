import cProfile, pstats, io
from pstats import SortKey


def run_profile(callback):
    pr = cProfile.Profile()
    pr.enable()
    try:
        callback()
    except KeyboardInterrupt:
        pass
    pr.disable()
    s = io.StringIO()
    sortby = SortKey.CUMULATIVE
    sortby = SortKey.TIME
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats(100)
    print(s.getvalue())
