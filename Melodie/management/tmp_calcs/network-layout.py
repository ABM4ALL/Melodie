# -*- coding:utf-8 -*-
# @Time: 2021/10/28 10:53
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: network-layout.py.py

import json
# import networkx as nx
import igraph

with open(r'C:\Users\12957\Documents\Developing\Python\melodie\Melodie\management\files\graph-demo.json') as f:
    d = json.load(f)

graph = igraph.Graph(directed=True)
# for node in d['series']['data']:
graph.add_vertices([node['id'] for node in d['series']['data']])

for edge in d['series']['links']:
    graph.add_edge(edge['source'], edge['target'])

# for node in d['series']['data']:
#     node_id = node['id']
#     graph.nodes[node_id]
#
layout = graph.layout_fruchterman_reingold(niter=2000)
print(layout)
for i, pos in enumerate(layout):
    print(i, pos)
# igraph.layout_fruchterman_reingold(graph)
# positions = nx.spring_layout(graph, k=0.01, iterations=1000)
# positions = nx.kamada_kawai_layout(graph)

for i, node_dict in enumerate(d['series']['data']):
    pos = layout[i]
    node_dict['x'], node_dict['y'] = pos[0], pos[1]
    node_dict['name'] = node_dict['id']
#
with open(r"C:\Users\12957\Documents\Developing\Python\melodie\Melodie\management\files\graph-demo-with-layout.json",
          "w") as f:
    json.dump(d, f, indent=4)
