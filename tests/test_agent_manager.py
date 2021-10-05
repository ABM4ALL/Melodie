from Melodie import Agent, AgentManager


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
    am = AgentManager(TestAgent, 0)
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
