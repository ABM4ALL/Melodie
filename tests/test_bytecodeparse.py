import math
from Melodie.basic import parse_watched_attrs


def test_parse_watched_attrs():
    f1 = lambda agent: agent.val + agent.text * 3 + math.acos(agent.val2)
    f2 = lambda agent: agent.val + agent.text.length * 3 + math.acos(agent.val2)

    def f3(agent):
        return agent.val + agent.text.length * 3 + math.acos(agent.val2)

    def f4(agent, arg2):
        return agent.val + agent.text.length * 3 + math.acos(agent.val2)

    def f5(agent, arg2=None):
        return agent.val + agent.text.length * 3 + math.acos(agent.val2)

    class A:
        def __init__(self):
            self.val = 0
            self.text = ""
            self.val2 = 1

        def a(self):
            return self.val + len(self.text) * 3 + math.acos(self.val2)

    def f6(agent):
        agent.val += 1

    assert set(parse_watched_attrs(f1)) == {"val", "text", "val2"}
    assert set(parse_watched_attrs(f2)) == {"val", "text", "val2"}
    assert set(parse_watched_attrs(f3)) == {"val", "text", "val2"}
    assert set(parse_watched_attrs(A().a)) == {"val", "text", "val2"}
    try:
        parse_watched_attrs(f4)
    except ValueError:
        pass

    try:
        parse_watched_attrs(f5)
    except ValueError:
        pass
