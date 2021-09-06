import os

import numpy as np
import pytest
from Melodie.Agent import Agent, decorator
from Melodie.basic import MelodieException


def test_params():
    class NewAgent(Agent):
        params = ["a", "b"]

        def __init__(self):
            super().__init__(None)
            self.a = 123
            self.b = 34.0

    agent = NewAgent()
    agent.set_params({"a": 456, "b": 34.0})
    assert agent.a == 456


def test_states_error_in_class_creation():
    """
    Try to create a state variable whose initial value was not in defined states.
    state 'xxxxxx' is not in possible states: {'open' , 'closed' , 'broken'}
    :return:
    """

    class AgentWithError(Agent):
        params = ["a", "b"]

        def __init__(self):
            super().__init__(None)
            self.status = 'xxxxxx'
            self.b = 34.0

        @Agent.decorator("status", ('closed', 'open'))
        def open(self):
            print('opened!')

        @Agent.decorator("status", ('open', 'closed'))
        def close(self):
            print('closed!')

        @Agent.decorator("status", ('closed', "broken"))
        def break_door(self):
            print('broke the door!')

    try:
        AgentWithError()
    except MelodieException as e:
        assert e.id == 1101


def test_states():
    class NewAgent(Agent):
        params = ["a", "b"]

        def __init__(self):
            super().__init__(None)
            self.status = 'open'  # 'open' , 'closed' and 'broken'
            self.b = 34.0

        @Agent.decorator("status", ('closed', 'open'))
        def open(self):
            print('opened!')

        @Agent.decorator("status", ('open', 'closed'))
        def close(self):
            print('closed!')

        @Agent.decorator("status", ('closed', "broken"))
        def break_door(self):
            print('broke the door!')

    new_agent = NewAgent()

    assert new_agent.status == 'open'
    new_agent.close()
    assert new_agent.status == 'closed'
    new_agent.break_door()
    assert new_agent.status == 'broken'
    try:
        new_agent.break_door()
    except MelodieException as e:
        assert e.id == 1102

    try:
        new_agent.status = 'xxxxxxx'
    except MelodieException as e:
        assert e.id == 1101  # 1101 stands for StateNotFoundError
        print(e)


# def drawCirc(ax, radius, centX, centY, angle_, theta2_, color_='black'):
#     import matplotlib.patches as patches
#     from numpy import radians as rad
#     # ========Line
#     arc = patches.Arc([centX, centY], radius, radius, angle=angle_,
#                       theta1=0, theta2=theta2_, capstyle='round', linestyle='-', color=color_)
#     ax.add_patch(arc)
#
#     # ========Create the arrow head
#     endX = centX + (radius / 2) * np.cos(rad(theta2_ + angle_))  # Do trig to determine end position
#     endY = centY + (radius / 2) * np.sin(rad(theta2_ + angle_))
#
#     ax.add_patch(  # Create triangle as arrow head
#         patches.RegularPolygon(
#             (endX, endY),  # (x,y)
#             3,  # number of vertices
#             radius / 9,  # radius
#             rad(angle_ + theta2_),  # orientation
#             color=color_
#         )
#     )
#     # ax.set_xlim([centX - radius, centY + radius]) and ax.set_ylim([centY - radius, centY + radius])
#     # Make sure you keep the axes scaled or else arrow will distort


def test_mermaid_md():
    md = """
    graph TD
    A[Client] -->|tcp_123| B(Load Balancer)
    B -->|tcp_456| C[Server1]
    B -->|tcp_456| D[Server2]
    A-->A
    """

    with open('../Melodie/static/mermaid.html', 'r') as f:
        html = f.read()
        html = html.replace('TEMPLATE', md)
        with open('out.html', 'w') as f:
            f.write(html)
            os.startfile('out.html')
    # print(html)


def test_nx_plot():
    class NewAgent(Agent):
        params = ["a", "b"]

        def __init__(self):
            super().__init__(None)
            self.status = 'open'  # 'open' , 'closed' and 'broken'
            self.b = 34.0

        @Agent.decorator("status", ('closed', 'open'))
        def open(self):
            print('opened!')

        @Agent.decorator("status", ('open', 'closed'))
        def close(self):
            print('closed!')

        @Agent.decorator("status", ('closed', "broken"))
        def break_door(self):
            print('broke the door!')

    new_agent = NewAgent()
    funcs = new_agent._state_funcs['status']
    watch = new_agent._state_watch['status']
    # s = {'0': {'1', '2', '0'}, '1': {'0', '1'}, '2': {'0', '2'}}

    graph_str = 'graph TD\n'
    for old_state, new_states in watch.items():
        for new_state in new_states:
            func = funcs[(old_state, new_state)]
            print(func.__qualname__)
            func_name = ".".join(func.__qualname__.rsplit('.', maxsplit=2)[-2:])
            graph_str += f'{old_state}-->|{func_name}|{new_state}\n'
    with open('../Melodie/static/mermaid.html', 'r') as f:
        html = f.read()
        html = html.replace('TEMPLATE', graph_str)
        with open('out.html', 'w') as f:
            f.write(html)
            os.startfile('out.html')
