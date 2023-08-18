import os

from MelodieInfra.static_analysis import StaticCheckerRoutine
dirname = os.path.dirname(__file__)
dir_to_analyse = os.path.join(dirname, "numba_demo")


def test_checker_numba():
    r = StaticCheckerRoutine(dir_to_analyse)
    r.run()
    assert len(r.messages) == 4
