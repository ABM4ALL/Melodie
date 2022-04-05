from Melodie import run_profile


def test_profiler():
    run_profile(lambda: print('aaa'))

    def kbd_exc_fcn():
        raise KeyboardInterrupt

    run_profile(kbd_exc_fcn)  # raise a keyboard interrupt exception inside
