import os

import numpy as np
import pytest
from Melodie.Agent import Agent
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

    new_agent = NewAgent()
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

    with open('../Melodie/static/mermaid.html','r') as f:
        html = f.read()
        html = html.replace('TEMPLATE',md)
        with open('out.html','w') as f:
            f.write(html)
            os.startfile('out.html')
    # print(html)

def test_nx_plot():
    s = {0: {1, 2, 0}, 1: {0, 1}, 2: {0, 2}}
    edges = []
    for old_state, new_states in s.items():
        for new_state in new_states:
            edges.append((old_state, new_state))

    import networkx as nx
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    G = nx.DiGraph()
    G.add_edges_from(edges)
    pos = nx.circular_layout(G)
    print(pos)
    # plt.axis('equal')
    fig = plt.figure()
    ax = fig.add_subplot(111, aspect='1')

    nodes = []
    x_range = [0, 1]
    y_range = [0, 1]
    r = 0.2
    font_compensation = 0.05
    for name, pos_arr in pos.items():
        print(pos_arr)
        p = ax.add_patch(
            patches.Circle(pos_arr - r, r)
        )
        nodes.append(p)
        x = pos_arr[0]
        y = pos_arr[1]
        plt.text(x - r -font_compensation, y - r-font_compensation, name, {'color': 'red',
                                      'size': 20, })
        if x < x_range[0]:
            x_range[0] = x - 2 * r
        elif x > x_range[1]:
            x_range[1] = x + 2 * r
        elif y < y_range[0]:
            y_range[0] = y - 2 * r
        elif y > y_range[1]:
            y_range[1] = y + 2 * r
    arrows = []
    for start, end in edges:
        start_pos = pos[start] - r
        end_pos = pos[end] - r
        vector = end_pos - start_pos
        style = "Simple,tail_width=0.5,head_width=4,head_length=8"
        kw = dict(arrowstyle=style, color="k")
        if np.linalg.norm(vector) <= 10 ** -4:
            print('aaaaaaaaa')
            new_pos = np.copy(start_pos)
            new_pos[1] += 0.1
            drawCirc(ax, 0.6, start_pos[0] - 0.5 * r, start_pos[1], 0, 360)
            # arrows.append(p := patches.FancyArrowPatch(start_pos + 0.05, start_pos - 0.05,
            #                                            connectionstyle="arc,angleA=0,armA=30,rad=1", **kw))
            # ax.add_patch(p)
        else:

            arrows.append(p := patches.FancyArrowPatch(start_pos, end_pos, connectionstyle="arc3,rad=.5", **kw))
            ax.add_patch(p)
        # plt.arrow(start_pos[0],start_pos[1] , vector[0], vector[1],
        #      width=0.01,
        #      length_includes_head=True,  # 增加的长度包含箭头部分
        #      # head_width=0.25,
        #      # head_length=1,
        #      fc='r',
        #      ec='b')

    print(G)
    # nx.draw(G,pos)
    plt.xlim(tuple(x_range))
    plt.ylim(tuple(y_range))
    plt.show()
