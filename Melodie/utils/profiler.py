import cProfile
import io
import pstats


def run_profile(callback):
    """
    Run a function with a profiler.
    When the callback finished or pressed Ctrl+C(KeyBoardInterrupt), the profile will be printed at the screen.
    :param callback:
    :return:
    """
    pr = cProfile.Profile()
    pr.enable()
    try:
        callback()
    except KeyboardInterrupt:
        pass
    pr.disable()
    s = io.StringIO()
    sortby = pstats.SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())
