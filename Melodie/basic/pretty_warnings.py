"""
Write prettified warnings to terminal for better focus attraction.
"""
# https://pypi.org/project/termcolor/
try:
    from termcolor import cprint
except:
    def cprint(s, **kwargs):
        print(s, **kwargs)
from .fsm import FSM


class ColorParseFSM(FSM):
    NORMAL = 0
    BOLD = 1
    UNDERLINE = 2
    REVERSE = 3
    SINGLE_STAR_FROM_NORMAL = 4
    SINGLE_STAR_FROM_BOLD = 5

    transitions = {
        NORMAL: {SINGLE_STAR_FROM_NORMAL, NORMAL, UNDERLINE, REVERSE},
        BOLD: {BOLD, NORMAL, SINGLE_STAR_FROM_BOLD},
        SINGLE_STAR_FROM_NORMAL: {BOLD, UNDERLINE},
        SINGLE_STAR_FROM_BOLD: {NORMAL},
        UNDERLINE: {UNDERLINE, NORMAL},
        REVERSE: {NORMAL, REVERSE}
    }

    def __init__(self):
        super().__init__(self.NORMAL, self.transitions)

    def on_star(self):
        d = {self.NORMAL: self.SINGLE_STAR_FROM_NORMAL,
             self.SINGLE_STAR_FROM_NORMAL: self.BOLD,
             self.BOLD: self.SINGLE_STAR_FROM_BOLD,
             self.SINGLE_STAR_FROM_BOLD: self.NORMAL,
             self.UNDERLINE: self.NORMAL}
        self.state_change(d[self.current_state])

    def on_back_quote(self):
        d = {self.NORMAL: self.REVERSE,
             self.REVERSE: self.NORMAL}
        self.state_change(d[self.current_state])

    def on_char(self):
        d = {
            self.SINGLE_STAR_FROM_NORMAL: self.UNDERLINE,
            self.NORMAL: self.NORMAL,
            self.BOLD: self.BOLD,
            self.UNDERLINE: self.UNDERLINE,
            self.REVERSE: self.REVERSE
        }
        self.state_change(d[self.current_state])

    def parse(self, content: str):
        for i, char in enumerate(content):
            if char == '*':
                self.on_star()
                continue
            elif char == '`':
                self.on_back_quote()
                continue
            else:
                self.on_char()
            if self.current_state == self.UNDERLINE:
                # cprint(char, on_color='on_yellow', attrs=['underline'], end="")
                cprint(char, color='grey', on_color='on_yellow', attrs=['underline'], end="")
            elif self.current_state == self.BOLD:
                cprint(char, color='grey', on_color='on_yellow', attrs=['bold'], end="")
            elif self.current_state == self.REVERSE:
                cprint(char, color='grey', on_color='on_yellow', attrs=['reverse'], end="")
            else:
                cprint(char, color='grey', on_color='on_yellow', end="")
        print('\n', end='')


import inspect


def show_link(stackdepth=1):
    """
     Print a link in PyCharm to a line in file.

     Thanks to: https://stackoverflow.com/questions/26300594/print-code-link-into-pycharms-console
    """

    file = inspect.stack()[stackdepth].filename
    line = inspect.stack()[stackdepth].lineno

    string = f'File "{file}", line {max(line, 1)}'.replace("\\", "/")
    return string


def show_prettified_warning(warning: str):
    ColorParseFSM().parse('WARNING: ' + warning)
