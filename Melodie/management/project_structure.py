# -*- coding:utf-8 -*-
# @Time: 2021/9/28 14:00
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test.py.py
import ast
import os
import sys
from typing import Dict, List, Set, Optional

import networkx as nx
from Melodie.management.pycfg import get_cfg, get_all_function_cfgs


def get_all_funcdefs(python_file: str) -> List[ast.FunctionDef]:
    f = open(python_file)
    source = f.read()
    f.close()
    root = ast.parse(source)
    function_defs: List[ast.FunctionDef] = []
    for node in ast.walk(root):
        if type(node) == ast.FunctionDef:
            function_defs.append(node)
    return function_defs


def list_all_files(parent_dir: str, ext_filter: Optional[Set[str]] = None) -> List[str]:
    """
    List all files in subdirectories recursively, matching the filter.
    :param parent_dir:
    :param ext_filter:
    :return:
    """
    if ext_filter is None:
        ext_filter = set()
    assert os.path.exists(parent_dir), f'Directory {parent_dir} not found!'
    all_files = []
    for root, dirs, files in os.walk(parent_dir):
        files = [file for file in files if os.path.splitext(file)[1] in ext_filter]
        for i, file in enumerate(files):
            file_abso_dir = os.path.join(root, file)
            files[i] = file_abso_dir
        all_files += files
    return all_files


def to_digraph(cfg: Dict) -> nx.DiGraph:
    g = nx.DiGraph()
    for k, v in cfg.items():
        g.add_node(k, source=v['excel_source'])
        for child in v['children']:
            g.add_edge(k, child)
    return g


def to_mermaid(g: nx.DiGraph) -> None:
    sources: Dict[int, str] = nx.get_node_attributes(g, 'excel_source')
    generated: List[str] = ['graph TD']
    for node in g.nodes:
        source = sources[node].replace('\"', "\'")
        generated.append(f"{node}[\"{source}\"]")

    for edge in g.edges:
        generated.append(f'{edge[0]}-->{edge[1]}')
    mermaid = '\n'.join(generated)

    with open('generated.html', 'w') as f_out:
        with open('../static/mermaid.html', 'r') as f:
            f_out.write(f.read().replace('TEMPLATE', mermaid))


if __name__ == '__main__':
    arcs = []
    cfgs = get_all_function_cfgs(
        r'C:\Users\12957\Documents\Developing\Python\melodie\examples\Wealth-Distribution-ParamFromExcel\WealthDistribution\modules\environment.py')
    print(len(cfgs))
    for f_cfg in cfgs:
        digraph = to_digraph(f_cfg)
        to_mermaid(digraph)
