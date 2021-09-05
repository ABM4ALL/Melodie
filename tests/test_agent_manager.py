import random

import time

from Melodie.Agent import Agent
from Melodie.AgentManager import AgentManager
from Melodie.basic import IndexedAgentList, SortedAgentIndex


class TestAgent(Agent):
    def setup(self):
        self.val = random.randint(0, 1000)
        self.text = "a" + str(self.val)
        # self.indiced = {("val",): lambda agent: agent.val}
        # self.mapped = {("text",): lambda agent: len(agent.text)}


class TestAgentManager(AgentManager):
    def setup(self):
        self.sorted_indices = {"val_index": lambda agent: agent.val}
        self.grouped_indices = {"text_index": lambda agent: len(agent.text)}


def test_sorted_agent_index2():
    length = random.randint(10, 10)
    agent_manager = TestAgentManager(TestAgent, length)
    agent = agent_manager.agents[random.randint(0, length - 1)]

    agent.val = -1
    assert len(agent_manager.indices_dict['val_index']) == length

    agent_manager.remove(agent)
    assert len(agent_manager) == length - 1
    assert len(agent_manager.indices_dict['val_index']) == length - 1
    assert agent_manager.indices_dict['text_index'].agent_count() == length - 1

    new_test_agent = TestAgent(agent_manager)
    new_test_agent.setup()
    new_test_agent.val = 10000
    agent_manager.add(new_test_agent)

    assert len(agent_manager) == length
    assert agent_manager.indices_dict['val_index'][-1].val == 10000


# def test_indexed_agent_list():
#     total_length = 500_00
#     # The test function is of O(n) complexity.
#     # Every loop it generates a list with length from 10 to 5000.
#     # every loop the total_length will be subtracted by the list length
#     # if it belows 0, exit test loop.
#     while 1:
#         length = random.randint(10, 5000)
#         if total_length < 0:
#             return
#         total_length -= length
#
#         agent_manager = AgentManager(TestAgent, length)
#
#         indexed_agent_list = IndexedAgentList(agent_manager.agents, )
#
#         new_test_agent = TestAgent(agent_manager)
#         new_test_agent.setup()
#
#         indexed_agent_list.add(new_test_agent)
#
#         assert len(indexed_agent_list.get_all_agents()) == length + 1
#         i = random.randint(0, length)
#         all_agents = indexed_agent_list.get_all_agents()
#         choosed_agent = all_agents[i]
#         choosed_agent.val = -1
#         assert choosed_agent.val == -1  # 确保正常赋值
#         indexed_agent_list.remove(choosed_agent)
#         assert len(indexed_agent_list.get_all_agents()) == length  # 测试移除Agent
#         for agent in indexed_agent_list.get_all_agents():
#             assert agent.val != -1  # make sure the agent 'new_test_agent' has been deleted
#
#
# def test_agent_group():
#     length = random.randint(10, 10)
#     agent_list = AgentManager(TestAgent, length)
#     agent = agent_list.agents[random.randint(0, length - 1)]
#     groups_dict = agent_list.groups
#     print(groups_dict[('text',)])
#     strlength = random.randint(7, 10)
#     assert strlength not in agent_list.groups[('text',)].group_names()
#     agent.text = 'a' * strlength
#
#     assert strlength in agent_list.groups[('text',)].group_names()
