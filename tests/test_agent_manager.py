import random

import pandas as pd

from Melodie import Agent, AgentList, GridAgent

from .config import model


class TestAgent(Agent):
    def setup(self):
        self.a = 0


def test_repr():
    ta = TestAgent(0)
    ta.setup()
    ret = repr(ta)
    print(ret)
    assert "<TestAgent " in ret
    assert "'a'" in ret
    assert "'id'" in ret
    assert isinstance(ta.id, int)


def test_agent_manager_type_hinting():
    ta = TestAgent(0)
    # ta.setup()
    am = AgentList(TestAgent, 0, model)
    am.add(ta, {"a": 0})
    ta_2 = TestAgent(1)
    # ta_2.setup()
    ta_2.a = 1
    am.add(ta_2, {"a": 1})
    assert am[0].a == 0
    assert am[1].a == 1

    assert len(am) == 2

    assert am.random_sample(1)[0].id in {ta.id, ta_2.id}

    df = am.to_dataframe(["a"])
    print(df)
    assert df.shape[0] == 2

    am.remove(ta)
    assert len(am) == 1
    assert am[0].a == 1


def test_properties():
    n = random.randint(10, 1000)
    al: AgentList[TestAgent] = AgentList(TestAgent, n, model)
    l = [j for j in range(n)]
    random.shuffle(l)
    df = pd.DataFrame([{"id": i, "a": random.randint(-100, 100)} for i in l])
    al.set_properties(df)
    for agent in al:
        assert agent.a == (df[df["id"] == agent.id]["a"].item())


def test_add_del_agents():
    n = 20
    al = AgentList(TestAgent, n, model)

    al.remove(al[10])
    al.add()
    assert al[-1].id == 20
    assert len(al) == 20
    for agent in al:
        assert al.get_agent(agent.id).id == agent.id
    new_agent = TestAgent(100)
    al.add(new_agent, {"id": 1000})


def test_agent_list_iteration():
    n = 20
    al = AgentList(TestAgent, n, model)
    times = 0
    for _ in al:
        l = [a.id for a in al]
        print(l)
        assert len(l) == len(al)
        times += 1
    assert times == len(al)


def test_properties_with_scenario():
    """
    Test when target scenario id is 100.

    The agent list should load the data with scenario_id==100, and should not load the data with scenario_id==0

    :return:
    """
    n = 10
    assert isinstance(model.scenario.id, int)
    al = AgentList(TestAgent, n, model)
    l = [j for j in range(n)]
    random.shuffle(l)
    df = pd.DataFrame(
        [{"id": i, "scenario_id": 0, "a": random.randint(-100, 100)} for i in l]
        + [
            {"id": i, "scenario_id": model.scenario.id, "a": random.randint(-100, 100)}
            for i in l
        ]
    )
    al.set_properties(df)
    assert len(al) == n
    df_scenario = df.query(f"scenario_id == {model.scenario.id}")
    for agent in al:
        assert agent.a == (df_scenario[df_scenario["id"] == agent.id]["a"].item())

    assert al.new_id() == 10
    print([a.id for a in al])


def test_grid_agents():
    al = AgentList(GridAgent, 10, model)
    al.to_list(["x"])
