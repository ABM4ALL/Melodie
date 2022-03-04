import cProfile
import pstats
import io


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
    # sortby = SortKey.CUMULATIVE
    sortby = pstats.SortKey.TIME
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats(100)
    print(s.getvalue())
