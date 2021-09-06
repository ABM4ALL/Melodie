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


def test_states():
    class NewAgent(Agent):
        params = ["a", "b"]

        def __init__(self):
            super().__init__(None)
            self.status = 0
            self.b = 34.0
            self.add_state_watch("status", {0: {1, 2}, 1: {0}, 2: {0}})

        @decorator((0,1))
        def f(self):
            print(123)

    new_agent = NewAgent()
    new_agent.f()
    new_agent.status = 1
    assert new_agent.status == 1
    try:
        new_agent.add_state_watch("status", {-1: {-1}})
    except MelodieException as e:
        assert e.id == 1101  # current state 1 is not in new state dict keys {-1}
        print(e)
    try:
        new_agent.status = 3
    except MelodieException as e:
        assert e.id == 1101  # 1101 stands for StateNotFoundError
        print(e)

    try:
        new_agent.status = 2
    except MelodieException as e:
        assert e.id == 1102  # 1101 stands for CannotMoveToNewStateError
        print(e)

    new_agent.status = 0
    assert new_agent.status == 0


def drawCirc(ax, radius, centX, centY, angle_, theta2_, color_='black'):
    import matplotlib.patches as patches
    from numpy import radians as rad
    # ========Line
    arc = patches.Arc([centX, centY], radius, radius, angle=angle_,
                      theta1=0, theta2=theta2_, capstyle='round', linestyle='-', color=color_)
    ax.add_patch(arc)

    # ========Create the arrow head
    endX = centX + (radius / 2) * np.cos(rad(theta2_ + angle_))  # Do trig to determine end position
    endY = centY + (radius / 2) * np.sin(rad(theta2_ + angle_))

    ax.add_patch(  # Create triangle as arrow head
        patches.RegularPolygon(
            (endX, endY),  # (x,y)
            3,  # number of vertices
            radius / 9,  # radius
            rad(angle_ + theta2_),  # orientation
            color=color_
        )
    )
    # ax.set_xlim([centX - radius, centY + radius]) and ax.set_ylim([centY - radius, centY + radius])
    # Make sure you keep the axes scaled or else arrow will distort


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
    s = {'0': {'1', '2', '0'}, '1': {'0', '1'}, '2': {'0', '2'}}
    graph_str = 'graph TD\n'
    for old_state, new_states in s.items():
        for new_state in new_states:
            graph_str += f'{old_state}-->{new_state}\n'
    with open('../Melodie/static/mermaid.html', 'r') as f:
        html = f.read()
        html = html.replace('TEMPLATE', graph_str)
        with open('out.html', 'w') as f:
            f.write(html)
            os.startfile('out.html')
