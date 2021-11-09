import random

import pandas as pd

from Melodie import Agent, AgentList

from .config import model


class TestAgent(Agent):
    def setup(self):
        self.a = 0


def test_repr():
    ta = TestAgent(0)
    ta.setup()
    ret = repr(ta)
    print(ret)
    assert '<TestAgent ' in ret
    assert '\'a\'' in ret
    assert '\'id\'' in ret


def test_agent_manager_type_hinting():
    ta = TestAgent(0)
    ta.setup()
    am = AgentList(TestAgent, 0, model)
    am.add(ta)
    ta_2 = TestAgent(1)
    ta_2.setup()
    ta_2.a = 1
    am.add(ta_2)
    for i, a in enumerate(am):
        assert a.a == i
    assert len(am) == 2

    assert am.random_sample(1)[0].id in {ta.id, ta_2.id}

    df = am.to_dataframe(['a'])
    print(df)
    assert df.shape[0] == 2

    am.remove(ta)
    assert len(am) == 1
    assert am[0].a == 1


def test_properties():
    n = random.randint(10, 1000)
    al = AgentList(TestAgent, n, model)
    l = [j for j in range(n)]
    random.shuffle(l)
    df = pd.DataFrame([
        {'id': i, "a": random.randint(-100, 100)} for i in l
    ])
    al.set_properties(df)
    for agent in al:
        assert agent.a == (df[df['id'] == agent.id]['a'].item())


def test_properties_with_scenario():
    n = random.randint(10,10)
    assert isinstance(model.scenario.id, int)
    al = AgentList(TestAgent, n, model)
    l = [j for j in range(n)]
    random.shuffle(l)
    df = pd.DataFrame([
                          {'id': i, "scenario_id": 0, "a": random.randint(-100, 100)} for i in l
                      ] + [
                          {'id': i, "scenario_id": model.scenario.id,
                           "a": random.randint(-100, 100)} for i in range(n)
                      ]
                      )
    al.set_properties(df)
    assert len(al) == n
    df_scenario = df.query(f"scenario_id == {model.scenario.id}")
    for agent in al:
        assert agent.a == (df_scenario[df_scenario['id'] == agent.id]['a'].item())
