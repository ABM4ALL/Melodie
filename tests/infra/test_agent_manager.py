import random
import pandas as pd
from Melodie import Agent, AgentList, GridAgent, set_seed, assert_exc_type_occurs
from MelodieInfra import GeneralTable
from sqlalchemy import Integer

from tests.infra.config import model


class TestAgent(Agent):
    def setup(self):
        self.a = 0


class TestAgentToFilter(Agent):
    def setup(self):
        self.a = 0
        self.b = 0.001


def test_repr():
    ta = TestAgent(0)
    ta.setup()
    ret = repr(ta)
    print(ret)
    assert "<TestAgent " in ret
    assert "'a'" in ret
    assert "'id'" in ret
    assert isinstance(ta.id, int)


def test_agent_manager_filter():
    am = AgentList(TestAgentToFilter, model)
    for i in range(10):
        ta = TestAgentToFilter(0)
        am.add(ta)
        ta.a = i
        ta.b = float(i)
    ret = am.filter(lambda agent: agent.a < 5 and agent.b > 2)

    assert len(ret) == 2


def test_agent_manager_type_hinting():
    ta = TestAgent(0)
    # ta.setup()
    am = AgentList(TestAgent, model)
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
    al: AgentList[TestAgent] = AgentList(TestAgent, model)
    l = [j for j in range(n)]
    random.shuffle(l)
    df = pd.DataFrame([{"id": i, "a": random.randint(-100, 100)} for i in l])
    table = GeneralTable.from_dicts(
        {"id": Integer(), "a": Integer()}, df.to_dict(orient="records")
    )

    def test_routine(t):
        al.set_properties(t)
        for agent in al:
            assert agent.a == (df[df["id"] == agent.id]["a"].item())

    test_routine(df)
    test_routine(table)


def test_add_del_agents():
    n = 20
    al = AgentList(TestAgent, model)
    al.setup_agents(n)
    al.remove(al[10])
    al.add()
    assert al[-1].id == 20
    assert len(al) == 20
    assert al.get_agent(21) is None
    assert al.get_agent(-1) is None
    for agent in al:
        assert al.get_agent(agent.id).id == agent.id
    new_agent = TestAgent(100)
    al.add(new_agent, {"id": 1000})
    ids = al.all_agent_ids()
    assert len(ids) == len(al.agents)


def test_repr_agent_manager():
    n = 20
    al = AgentList(TestAgent, model)
    al.setup_agents(n)
    repr(al)  # Not check


# def test_add_del_agents_dict():
#     n = 20
#     al = AgentDict(TestAgent, n, model)
#     al.remove(al[10])
#     al.add()
#     assert len(al) == 20
#     for agent in al:
#         assert al.get_agent(agent.id).id == agent.id
#     new_agent = TestAgent(100)
#     al.add(new_agent, {"id": 1000})


def test_agent_list_iteration():
    n = 20
    al = AgentList(TestAgent, model)
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

    The agent list should load the data with id_scenario==100, and should not load the data with id_scenario==0

    :return:
    """
    n = 10
    assert isinstance(model.scenario.id, int)
    for al in [AgentList(TestAgent, model)]:
        l = [j for j in range(n)]
        random.shuffle(l)
        df = pd.DataFrame(
            [{"id": i, "id_scenario": 0, "a": random.randint(-100, 100)} for i in l]
            + [
                {
                    "id": i,
                    "id_scenario": model.scenario.id,
                    "a": random.randint(-100, 100),
                }
                for i in l
            ]
        )
        al.setup_agents(n, df)
        assert len(al) == n
        df_scenario = df.query(f"id_scenario == {model.scenario.id}")
        for agent in al:
            assert agent.a == (df_scenario[df_scenario["id"] == agent.id]["a"].item())

        assert al.new_id() == 10
        print([a.id for a in al])


def test_grid_agents():
    class GridAgent1(GridAgent):
        def set_category(self):
            self.category = 0

    al = AgentList(GridAgent1, model)
    al.setup_agents(10)
    al.to_list(["x"])


def test_random_sample_seed():
    set_seed(5)

    al = AgentList(Agent, model)
    al.setup_agents(10)
    a1, a2 = al.random_sample(2)
    print(a1.id, a2.id)
