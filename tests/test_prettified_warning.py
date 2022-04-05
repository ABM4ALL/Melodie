import sys
sys.path.append("/Users/hzy/Documents/Projects/MelodieABM/Melodie")
from Melodie.basic.pretty_warnings import ColorParseFSM, show_link


def test_prettified_print():
    ColorParseFSM().parse('This is **warning** *message* `aps dddddd`!!!!')
    print(show_link())
