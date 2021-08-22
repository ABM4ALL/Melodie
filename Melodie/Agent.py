from typing import List, Dict, Any

from Melodie.Element import Element


class Agent(Element):
    def __init__(self):
        """
        __init__method contains no parameter.
        """

    def fibonacci(self, n, a=0, b=1):
        if n == 0:  # edge case
            return a
        if n == 1:  # usual base case
            return b
        return self.fibonacci(n - 1, b, a + b)
