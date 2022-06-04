import json

import numpy as np

from Melodie import Agent
from Melodie.boost.vectorize import vectorize, vectorize_2d, apply, apply_2d


class NewAgent(Agent):
    def __init__(self, id):
        super(NewAgent, self).__init__(id)
        self.a = 1.0 * id


def test_1d():
    agents = [NewAgent(i) for i in range(100)]
    v = vectorize(agents, "id")
    assert tuple(v) == tuple([i for i in range(100)])
    props = [i for i in range(99, -1, -1)]
    apply(agents, "id", np.array(props))
    assert tuple(vectorize(agents, "id")) == tuple(props)

    v = vectorize(agents, "a")
    assert tuple(v) == tuple([i * 1.0 for i in range(100)])
    props2 = [i * 1.0 for i in range(99, -1, -1)]
    apply(agents, "a", np.array(props2))
    assert tuple(vectorize(agents, "id")) == tuple(props2)


def test_2d():
    agents = [[NewAgent(i * 10 + j) for i in range(10)] for j in range(10)]
    props = [[i * 10 + j for i in range(10)] for j in range(10)]
    props_int_2 = [[i * 10 + j for i in range(10)] for j in range(9, -1, -1)]
    props_float = [[(i * 10 + j) * 1.0 for i in range(10)] for j in range(10)]
    props_float_2 = [[(i * 10 + j) * 1.0 for i in range(10)] for j in range(9, -1, -1)]
    v = vectorize_2d(agents, "id")
    print(v)
    assert json.dumps(vectorize_2d(agents, "id").tolist()) == json.dumps(props)
    assert json.dumps(vectorize_2d(agents, "a").tolist()) == json.dumps(props_float)

    apply_2d(agents, "a", np.array(props_float_2))
    apply_2d(agents, "id", np.array(props_int_2))

    assert json.dumps(vectorize_2d(agents, "id").tolist()) == json.dumps(props_int_2)
    assert json.dumps(vectorize_2d(agents, "a").tolist()) == json.dumps(props_float_2)
