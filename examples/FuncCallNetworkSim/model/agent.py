# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from Melodie import Agent


class FuncAgent(Agent):
    """
    FuncAgent acts as the node from the
    TODO: Forbid user rewriting id and other reserved properties in setup() function!
    """

    def setup(self):
        self.reliability = 0.99
        self.status = 0
        self._status_next = 0

    def update(self):
        self.status = self._status_next

    def recover(self):
        """
        Recover from failure
        :return:
        """
        self._status_next = 0

    def fail(self):
        """

        :return:
        """
        self._status_next = 1
