# -*- coding:utf-8 -*-
# @Time: 2021/10/8 13:54
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: astdemo.py.py

class PseudoAgent:
    """
    This is a pseudo agent simulating an Agent class
    with some properties and common ways.
    """

    def setup(self):
        self.id = 0
        self.account = 0.0
        self.productivity = 0.0
        self.x = 1

    def demofunction(self):

        rand = np.random.uniform(0, 1)
        if rand <= self.productivity:
            self.account += 1
        else:
            pass

        return None

    def demofunction2(self):
        """
        This function mainly tests or
        :return:
        """

        rand = np.random.uniform(0, 1)
        if rand <= self.productivity:
            self.account, self.x = 1, 2
        else:
            pass

        return None

    def test_tuple_parse(self):
        """
        This function mainly tests or
        :return:
        """

        rand = np.random.uniform(0, 1)
        self.x = (1, 2, 3)
        y = [1, 2, 3]
        z = {1, 2, 3}
        w = {'a': 1, 'b': 2, 'c': 3}
        if rand <= self.productivity:
            self.account, self.x = 1, 2
        else:
            pass

        return None

    def test_enclosures(self):
        """
        This function mainly tests enclosure.

        Behavior: it will not show enclosure definition.
        :return:
        """

        def f():
            return np.random.uniform(0, 1)

        rand = f()
        if rand <= self.productivity:
            self.account, self.x = 1, 2
        else:
            pass

        return None

    def test_loops(self):
        """
        Test While and For Loops
        :return:
        """
        for i in range(self.x):
            self.y += i

        while i > 0:
            i -= 1
            self.y -= 0.6 * i
