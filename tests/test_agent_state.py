# import os
#
# import numpy as np
# import pytest
# from Melodie.Agent import Agent, decorator
# from Melodie.basic import MelodieException
#
#
# def test_params():
#     class NewAgent(Agent):
#         params = ["a", "b"]
#
#         def __init__(self):
#             super().__init__(None)
#             self.a = 123
#             self.b = 34.0
#
#     agent = NewAgent()
#     agent.set_params({"a": 456, "b": 34.0})
#     assert agent.a == 456
#
#
# def test_states_error_in_class_creation():
#     """
#     Try to create a state variable whose initial value was not in defined states.
#     state 'xxxxxx' is not in possible states: {'open' , 'closed' , 'broken'}
#     :return:
#     """
#
#     class AgentWithError(Agent):
#         params = ["a", "b"]
#
#         def __init__(self):
#             super().__init__(None)
#             self.status = 'xxxxxx'
#             self.b = 34.0
#
#         @Agent.state_transition("status", ('closed', 'open'))
#         def open(self):
#             print('opened!')
#             return True
#
#         @Agent.state_transition("status", ('open', 'closed'))
#         def close(self):
#             print('closed!')
#             return True
#
#         @Agent.state_transition("status", ('closed', "broken"))
#         def break_door(self):
#             print('broke the door!')
#             return True
#
#     try:
#         AgentWithError()
#     except MelodieException as e:
#         assert e.id == 1101
#
#
# def test_states():
#     class NewAgent(Agent):
#         params = ["a", "b"]
#
#         def __init__(self):
#             super().__init__(None)
#             self.status = 'open'  # 'open' , 'closed' and 'broken'
#             self.b = 34.0
#
#         @Agent.state_transition("status", ('closed', 'open'))
#         def open(self):
#             print('opened!')
#             return True
#
#         @Agent.state_transition("status", ('open', 'closed'))
#         def close(self):
#             print('closed!')
#             return True
#
#         @Agent.state_transition("status", ('closed', "broken"))
#         def break_door(self):
#             print('broke the door!')
#             return True
#
#     new_agent = NewAgent()
#
#     assert new_agent.status == 'open'
#     new_agent.close()
#     assert new_agent.status == 'closed'
#     new_agent.break_door()
#     assert new_agent.status == 'broken'
#     try:
#         new_agent.break_door()
#     except MelodieException as e:
#         assert e.id == 1102
#
#     try:
#         new_agent.status = 'xxxxxxx'
#     except MelodieException as e:
#         assert e.id == 1101  # 1101 stands for StateNotFoundError
#         print(e)
#
#     assert new_agent.current_state_is('status', 'broken')
#     assert not new_agent.current_state_is('status', 'closed')
#     try:
#         new_agent.current_state_is('statusxxx', '')  # Unexisted attribute statusxxx
#     except MelodieException as e:
#         assert e.id == 1103
#     try:
#         new_agent.current_state_is('b', '')  # Existed attribute b, but b is not state attribute
#     except MelodieException as e:
#         assert e.id == 1103
#     try:
#         new_agent.current_state_is('status', 'x')  # Existed state attribute status, but state `x` is not found
#     except MelodieException as e:
#         assert e.id == 1101
#
#
# def test_mermaid_md():
#     md = """
#     graph TD
#     A[Client] -->|tcp_123| B(Load Balancer)
#     B -->|tcp_456| C[Server1]
#     B -->|tcp_456| D[Server2]
#     A-->A
#     """
#
#     with open('../Melodie/static/mermaid.html', 'r') as f:
#         html = f.read()
#         html = html.replace('TEMPLATE', md)
#         with open('out.html', 'w') as f:
#             f.write(html)
#             os.startfile('out.html')
#     # print(html)
#
#
# def test_nx_plot():
#     class NewAgent(Agent):
#         params = ["a", "b"]
#
#         def __init__(self):
#             super().__init__(None)
#             self.status = 'open'  # 'open' , 'closed' and 'broken'
#             self.b = 34.0
#
#         @Agent.state_transition("status", ('closed', 'open'))
#         def open(self):
#             print('opened!')
#             return True
#
#         @Agent.state_transition("status", ('open', 'closed'))
#         def close(self):
#             print('closed!')
#             return True
#
#         @Agent.state_transition("status", ('closed', "broken"))
#         def break_door(self):
#             print('broke the door!')
#             return True
#
#     new_agent = NewAgent()
#     funcs = new_agent._state_funcs['status']
#     watch = new_agent._state_watch['status']
#     # s = {'0': {'1', '2', '0'}, '1': {'0', '1'}, '2': {'0', '2'}}
#
#     graph_str = 'graph TD\n'
#     for old_state, new_states in watch.items():
#         for new_state in new_states:
#             func = funcs[(old_state, new_state)]
#             print(func.__qualname__)
#             func_name = ".".join(func.__qualname__.rsplit('.', maxsplit=2)[-2:])
#             graph_str += f'{old_state}-->|{func_name}|{new_state}\n'
#     with open('../Melodie/static/mermaid.html', 'r') as f:
#         html = f.read()
#         html = html.replace('TEMPLATE', graph_str)
#         with open('out.html', 'w') as f:
#             f.write(html)
#             os.startfile('out.html')
