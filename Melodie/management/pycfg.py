"""
#!/usr/bin/env python3
# Author: Rahul Gopinath <rahul.gopinath@cispa.saarland>
# License: GPLv3
"""

import ast
import re
from typing import List, Dict, Union, Tuple

import astunparse


class CFGNode(dict):
    registry = 0
    cache = {}
    stack = []
    tagged_edges: Dict[Tuple[int, int], str] = {}

    def __init__(self, parents=[], ast=None):
        assert type(parents) is list
        self.parents = parents
        self.calls = []
        self.children = []
        self.ast_node = ast
        self.rid = CFGNode.registry
        # self.entry_status = None
        CFGNode.cache[self.rid] = self
        CFGNode.registry += 1

    def lineno(self):
        return self.ast_node.lineno if hasattr(self.ast_node, 'lineno') else 0

    def __str__(self):
        return "id:%d line[%d] parents: %s : %s" % (
            self.rid, self.lineno(), str([p.rid for p in self.parents]), self.source())

    def __repr__(self):
        return str(self)

    def add_child(self, c):
        if c not in self.children:
            self.children.append(c)

    def __eq__(self, other):
        return self.rid == other.rid

    def __neq__(self, other):
        return self.rid != other.rid

    def set_parents(self, p):
        self.parents = p

    def add_parent(self, p):
        if p not in self.parents:
            self.parents.append(p)

    def add_parents(self, ps):
        for p in ps:
            self.add_parent(p)

    def add_calls(self, func):
        self.calls.append(func)

    def source(self):
        return astunparse.unparse(self.ast_node).strip()

    def to_json(self):
        return {'id': self.rid, 'parents': [p.rid for p in self.parents], 'children': [c.rid for c in self.children],
                'calls': self.calls, 'at': self.lineno(), 'ast': self.source(),
                }

    @classmethod
    def to_graph(cls, arcs=[]):
        def unhack(v):
            for i in ['if', 'while', 'for', 'elif']:
                v = re.sub(r'^_%s:' % i, '%s:' % i, v)
            return v

        nodes = []
        for nid, cnode in CFGNode.cache.items():
            nodes.append(cnode)
        return nodes
        G = pygraphviz.AGraph(directed=True)
        cov_lines = set(i for i, j in arcs)
        for nid, cnode in CFGNode.cache.items():
            G.add_node(cnode.rid)
            n = G.get_node(cnode.rid)
            lineno = cnode.lineno()
            n.attr['label'] = "%d: %s" % (lineno, unhack(cnode.source()))
            for pn in cnode.parents:
                plineno = pn.lineno()
                if hasattr(pn, 'calllink') and pn.calllink > 0 and not hasattr(cnode, 'calleelink'):
                    G.add_edge(pn.rid, cnode.rid, style='dotted', weight=100)
                    continue

                if arcs:
                    if (plineno, lineno) in arcs:
                        G.add_edge(pn.rid, cnode.rid, color='blue')
                    elif plineno == lineno and lineno in cov_lines:
                        G.add_edge(pn.rid, cnode.rid, color='blue')
                    elif hasattr(cnode, 'fn_exit_node') and plineno in cov_lines:  # child is exit and parent is covered
                        G.add_edge(pn.rid, cnode.rid, color='blue')
                    elif hasattr(pn, 'fn_exit_node') and len(set(n.lineno() for n in
                                                                 pn.parents) | cov_lines) > 0:  # parent is exit and one of its parents is covered.
                        G.add_edge(pn.rid, cnode.rid, color='blue')
                    elif plineno in cov_lines and hasattr(cnode,
                                                          'calleelink'):  # child is a callee (has calleelink) and one of the parents is covered.
                        G.add_edge(pn.rid, cnode.rid, color='blue')
                    else:
                        G.add_edge(pn.rid, cnode.rid, color='red')
                else:
                    G.add_edge(pn.rid, cnode.rid)
        return G


class PyCFG:
    """
    The python CFG
    """

    def __init__(self):
        self.founder = CFGNode(parents=[], ast=ast.parse('start').body[0])  # sentinel
        self.founder.ast_node.lineno = 0
        self.functions = {}
        self.functions_node = {}

    def parse(self, src):
        return ast.parse(src)

    def walk(self, node, myparents):
        if node is None: return
        fname = "on_%s" % node.__class__.__name__.lower()
        if hasattr(self, fname):
            fn = getattr(self, fname)
            v = fn(node, myparents)
            return v
        else:
            if fname[3:] in {'constant', 'name', 'attribute',
                             'tuple', 'list', 'set', 'dict'}:
                return myparents
            else:
                print(fname, ast.dump(node))
                return myparents

    def on_module(self, node, myparents):
        """
        Module(stmt* body)
        """
        # each time a statement is executed unconditionally, make a link from
        # the result to next statement
        p = myparents
        for n in node.body:
            p = self.walk(n, p)
        return p

    def on_assign(self, node, myparents):
        """
        Assign(expr* targets, expr value)

        It seems that parallel assignment was not implemented in Python 3.8

        -- 'simple' indicates that we annotate simple name without parens
        TODO: AnnAssign(expr target, expr annotation, expr? value, int simple)
        """
        # if len(node.targets) > 1: raise NotImplemented('Parallel assignments')

        p = [CFGNode(parents=myparents, ast=node)]
        p = self.walk(node.value, p)

        return p

    def on_augassign(self, node, myparents):
        """
        ast.AugAssign
        AugAssign(expr target, operator op, expr value)
        :param node:
        :param myparents:
        :return:
        """
        # if len(node.target) > 1: raise NotImplemented('Parallel assignments')

        p = [CFGNode(parents=myparents, ast=node)]
        p = self.walk(node.value, p)

        return p

    def on_pass(self, node, myparents):
        return [CFGNode(parents=myparents, ast=node)]

    def on_break(self, node, myparents):
        parent = myparents[0]
        while not hasattr(parent, 'exit_nodes'):
            # we have ordered parents
            parent = parent.parents[0]

        assert hasattr(parent, 'exit_nodes')
        p = CFGNode(parents=myparents, ast=node)

        # make the break one of the parents of label node.
        parent.exit_nodes.append(p)

        # break doesnt have immediate children
        return []

    def on_continue(self, node, myparents):
        parent = myparents[0]
        while not hasattr(parent, 'exit_nodes'):
            # we have ordered parents
            parent = parent.parents[0]
        assert hasattr(parent, 'exit_nodes')
        p = CFGNode(parents=myparents, ast=node)

        # make continue one of the parents of the original test node.
        parent.add_parent(p)

        # return the parent because a continue is not the parent
        # for the just next node
        return []

    def on_for(self, node, myparents):
        # node.target in node.iter: node.body
        _test_node = CFGNode(parents=myparents,
                             ast=ast.parse('_for: True if %s else False' % astunparse.unparse(node.iter).strip()).body[
                                 0])
        ast.copy_location(_test_node.ast_node, node)

        # we attach the label node here so that break can find it.
        _test_node.exit_nodes = []
        test_node = self.walk(node.iter, [_test_node])

        extract_node = CFGNode(parents=[_test_node], ast=ast.parse(
            '%s = %s.shift()' % (astunparse.unparse(node.target).strip(), astunparse.unparse(node.iter).strip())).body[
            0])
        ast.copy_location(extract_node.ast_node, _test_node.ast_node)

        # now we evaluate the body, one at a time.
        p1 = [extract_node]
        for n in node.body:
            p1 = self.walk(n, p1)

        # the test node is looped back at the end of processing.
        _test_node.add_parents(p1)

        return _test_node.exit_nodes + test_node

    def on_while(self, node, myparents):
        # For a while, the earliest parent is the node.test
        _test_node = CFGNode(parents=myparents,
                             ast=ast.parse('_while: %s' % astunparse.unparse(node.test).strip()).body[0])
        ast.copy_location(_test_node.ast_node, node.test)
        _test_node.exit_nodes = []
        test_node = self.walk(node.test, [_test_node])

        # we attach the label node here so that break can find it.

        # now we evaluate the body, one at a time.
        p1 = test_node
        for n in node.body:
            p1 = self.walk(n, p1)

        # the test node is looped back at the end of processing.
        _test_node.add_parents(p1)

        # link label node back to the condition.
        return _test_node.exit_nodes + test_node

    def on_if(self, node, myparents):
        _test_node = CFGNode(parents=myparents,
                             ast=ast.parse('_if: %s' % astunparse.unparse(node.test).strip()).body[0])
        ast.copy_location(_test_node.ast_node, node.test)
        test_node = self.walk(node.test, [_test_node])
        g1: List[CFGNode] = test_node
        saved = False
        for i, n in enumerate(node.body):
            g1 = self.walk(n, g1)
            if i == 0 and len(g1) > 0 and (not saved):
                parent: CFGNode = _test_node
                if parent.rid != g1[0].rid:
                    CFGNode.tagged_edges[(parent.rid, g1[0].rid)] = 'true'
                    saved = True

        g2 = test_node
        for i, n in enumerate(node.orelse):
            g2 = self.walk(n, g2)
            if i == 0 and len(g2) > 0:
                parent: CFGNode = g2[0].parents[0]
                CFGNode.tagged_edges[(parent.rid, g2[0].rid)] = 'false'

        return g1 + g2

    def on_binop(self, node, myparents):
        left = self.walk(node.left, myparents)
        right = self.walk(node.right, left)
        return right

    def on_compare(self, node, myparents):
        left = self.walk(node.left, myparents)
        right = self.walk(node.comparators[0], left)
        return right

    def on_unaryop(self, node, myparents):
        return self.walk(node.operand, myparents)

    def on_call(self, node, myparents):
        def get_func(node):
            if type(node.func) is ast.Name:
                mid = node.func.id
            elif type(node.func) is ast.Attribute:
                mid = node.func.attr
            elif type(node.func) is ast.Call:
                mid = get_func(node.func)
            else:
                raise Exception(str(type(node.func)))
            return mid
            # mid = node.func.value.id

        p = myparents
        for a in node.args:
            p = self.walk(a, p)
        mid = get_func(node)
        myparents[0].add_calls(mid)

        # these need to be unlinked later if our module actually defines these
        # functions. Otherwsise we may leave them around.
        # during a call, the direct child is not the next
        # statement in text.
        for c in p:
            c.calllink = 0
        return p

    def on_expr(self, node, myparents):
        p = [CFGNode(parents=myparents, ast=node)]
        return self.walk(node.value, p)

    def on_return(self, node, myparents):
        parent = myparents[0]

        val_node = self.walk(node.value, myparents)
        # on return look back to the function definition.
        while not hasattr(parent, 'return_nodes'):
            parent = parent.parents[0]
        assert hasattr(parent, 'return_nodes')

        p = CFGNode(parents=val_node, ast=node)

        # make the break one of the parents of label node.
        parent.return_nodes.append(p)

        # return doesnt have immediate children
        return []

    def on_functiondef(self, node, myparents):
        # a function definition does not actually continue the thread of
        # control flow
        # name, args, body, decorator_list, returns
        fname = node.name
        args = node.args
        returns = node.returns

        enter_node = CFGNode(parents=[], ast=
        ast.parse('enter: %s(%s)' % (node.name, ', '.join([a.arg for a in node.args.args]))).body[0])  # sentinel
        enter_node.calleelink = True
        ast.copy_location(enter_node.ast_node, node)
        exit_node = CFGNode(parents=[], ast=
        ast.parse('exit: %s(%s)' % (node.name, ', '.join([a.arg for a in node.args.args]))).body[0])  # sentinel
        exit_node.fn_exit_node = True
        ast.copy_location(exit_node.ast_node, node)
        enter_node.return_nodes = []  # sentinel

        p = [enter_node]
        for n in node.body:
            p = self.walk(n, p)

        for n in p:
            if n not in enter_node.return_nodes:
                enter_node.return_nodes.append(n)

        for n in enter_node.return_nodes:
            exit_node.add_parent(n)

        self.functions[fname] = [enter_node, exit_node]
        self.functions_node[enter_node.lineno()] = fname

        return myparents

    def get_defining_function(self, node):
        if node.lineno() in self.functions_node: return self.functions_node[node.lineno()]
        if not node.parents:
            self.functions_node[node.lineno()] = ''
            return ''
        val = self.get_defining_function(node.parents[0])
        self.functions_node[node.lineno()] = val
        return val

    def link_functions(self):
        for nid, node in CFGNode.cache.items():
            if node.calls:
                for calls in node.calls:
                    if calls in self.functions:
                        enter, exit = self.functions[calls]
                        enter.add_parent(node)
                        if node.children:
                            # # until we link the functions up, the node
                            # # should only have succeeding node in text as
                            # # children.
                            # assert(len(node.children) == 1)
                            # passn = node.children[0]
                            # # We require a single pass statement after every
                            # # call (which means no complex expressions)
                            # assert(type(passn.ast_node) == ast.Pass)

                            # # unlink the call statement
                            assert node.calllink > -1
                            node.calllink += 1
                            for i in node.children:
                                i.add_parent(exit)
                            # passn.set_parents([exit])
                            # ast.copy_location(exit.ast_node, passn.ast_node)

                            # #for c in passn.children: c.add_parent(exit)
                            # #passn.ast_node = exit.ast_node

    def update_functions(self):
        for nid, node in CFGNode.cache.items():
            _n = self.get_defining_function(node)

    def update_children(self):
        for nid, node in CFGNode.cache.items():
            for p in node.parents:
                p.add_child(node)

    def gen_cfg(self, src):
        """
        >>> i = PyCFG()
        >>> i.walk("100")
        5
        """
        node = self.parse(src)
        for f in ast.walk(node):
            if isinstance(f, ast.FunctionDef):
                print(f)
                node = f

        nodes = self.walk(node, [self.founder])
        self.last_node = CFGNode(parents=nodes, ast=ast.parse('stop').body[0])
        ast.copy_location(self.last_node.ast_node, self.founder.ast_node)
        self.update_children()
        self.update_functions()
        self.link_functions()

    def gen_cfg_from_function_ast(self, func_ast: ast.FunctionDef):
        nodes = self.walk(func_ast, [self.founder])
        self.last_node = CFGNode(parents=nodes, ast=ast.parse('stop').body[0])
        ast.copy_location(self.last_node.ast_node, self.founder.ast_node)
        self.update_children()
        self.update_functions()
        self.link_functions()

    def get_all_function_asts(self, src: str) -> List[ast.FunctionDef]:
        node = self.parse(src)
        functions: List[ast.FunctionDef] = []
        for f in ast.walk(node):
            if isinstance(f, ast.FunctionDef):
                functions.append(f)
        return functions


def compute_dominator(cfg, start=0, key='parents'):
    dominator = {}
    dominator[start] = {start}
    all_nodes = set(cfg.keys())
    rem_nodes = all_nodes - {start}
    for n in rem_nodes:
        dominator[n] = all_nodes

    c = True
    while c:
        c = False
        for n in rem_nodes:
            pred_n = cfg[n][key]
            doms = [dominator[p] for p in pred_n]
            i = set.intersection(*doms) if doms else set()
            v = {n} | i
            if dominator[n] != v:
                c = True
            dominator[n] = v
    return dominator


def slurp(f):
    with open(f, 'r') as f: return f.read()


# def parse_graph(cfg: PyCFG, cache: Dict[str, Dict[str, Union[str, int]]]) -> Dict:
#     g = {}
#     for k, v in cache.items():
#         j = v.to_json()
#         at = j['at']
#
#         parents_at = [cache[p].to_json()['at'] for p in j['parents']]
#         children_at = [cache[c].to_json()['at'] for c in j['children']]
#         if at not in g:
#             g[at] = {'parents': set(), 'children': set()}
#         # remove dummy nodes
#         ps = set([p for p in parents_at if p != at])
#         cs = set([c for c in children_at if c != at])
#         g[at]['parents'] |= ps
#         g[at]['children'] |= cs
#         if v.calls:
#             g[at]['calls'] = v.calls
#         g[at]['function'] = cfg.functions_node[v.lineno()]
#         g[at]['excel_source'] = cache[k].excel_source()
#     return g

def parse_graph(cfg: PyCFG, cache: Dict[str, Dict[str, Union[str, int]]]) -> Dict:
    g = {}
    for k, v in cache.items():
        j = v.to_json()
        # print(j)
        at = j['at']
        node_id = j['id']

        parents_id = [cache[p].to_json()['id'] for p in j['parents']]
        children_id = [cache[c].to_json()['id'] for c in j['children']]
        if node_id not in g:
            g[node_id] = {'parents': set(), 'children': set()}
        # remove dummy nodes
        ps = set([p for p in parents_id if p != node_id])
        cs = set([c for c in children_id if c != node_id])
        g[node_id]['parents'] |= ps
        g[node_id]['children'] |= cs
        if v.calls:
            g[node_id]['calls'] = v.calls
        g[node_id]['function'] = cfg.functions_node[v.lineno()]
        g[node_id]['excel_source'] = cache[k].source()
    return g


def get_function_cfg(function: ast.FunctionDef) -> Tuple[Dict, Dict]:
    cfg = PyCFG()
    # graph: Dict = {}
    CFGNode.cache = {}
    CFGNode.stack = []
    CFGNode.registry = 0
    CFGNode.tagged_edges = {}
    # print(CFGNode.registry)
    cfg = PyCFG()
    cfg.gen_cfg_from_function_ast(function)
    # print(CFGNode.registry)
    print(CFGNode.tagged_edges)
    g = parse_graph(cfg, CFGNode.cache)
    return g, CFGNode.tagged_edges


def get_all_function_cfgs(pythonfile):
    cfg = PyCFG()
    functions = cfg.get_all_function_asts(slurp(pythonfile).strip())
    graphs: List[Dict] = []
    for func_ast in functions:
        CFGNode.cache = {}
        CFGNode.stack = []
        CFGNode.tagged_edges = {}
        CFGNode.registry = 0
        print(CFGNode.registry)
        cfg = PyCFG()
        cfg.gen_cfg_from_function_ast(func_ast)
        print(CFGNode.registry)
        # print(CFGNode.cache)
        g = parse_graph(cfg, CFGNode.cache)
        graphs.append(g)

    return graphs


def get_cfg(pythonfile):
    cfg = PyCFG()
    cfg.gen_cfg(slurp(pythonfile).strip())
    cache = CFGNode.cache
    print(cache)
    g = {}
    g['edge_tags'] = CFGNode.tagged_edges
    for k, v in cache.items():
        j = v.to_json()
        at = j['at']

        parents_at = [cache[p].to_json()['at'] for p in j['parents']]
        children_at = [cache[c].to_json()['at'] for c in j['children']]
        if at not in g:
            g[at] = {'parents': set(), 'children': set()}
        # remove dummy nodes
        ps = set([p for p in parents_at if p != at])
        cs = set([c for c in children_at if c != at])
        g[at]['parents'] |= ps
        g[at]['children'] |= cs
        if v.calls:
            g[at]['calls'] = v.calls
        g[at]['function'] = cfg.functions_node[v.lineno()]
        g[at]['excel_source'] = cache[k].source()
    return (g, cfg.founder.ast_node.lineno, cfg.last_node.ast_node.lineno)


def compute_flow(pythonfile):
    cfg, first, last = get_cfg(pythonfile)
    return cfg, compute_dominator(cfg, start=first), compute_dominator(cfg, start=last, key='children')


if __name__ == '__main__':
    import json
    import sys
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('pythonfile', help='The python data to be analyzed')
    parser.add_argument('-d', '--dots', action='store_true', help='generate a dot data')
    parser.add_argument('-c', '--cfg', action='store_true', help='print cfg')
    parser.add_argument('-x', '--coverage', action='store', dest='coverage', type=str, help='branch coverage data')
    parser.add_argument('-y', '--ccoverage', action='store', dest='ccoverage', type=str, help='custom coverage data')
    args = parser.parse_args()
    if args.dots:
        arcs = None
        if args.coverage:
            cdata = coverage.CoverageData()
            cdata.read_file(filename=args.coverage)
            arcs = [(abs(i), abs(j)) for i, j in cdata.arcs(cdata.measured_files()[0])]
        elif args.ccoverage:
            arcs = [(i, j) for i, j in json.loads(open(args.ccoverage).read())]
        else:
            arcs = []
        cfg = PyCFG()
        cfg.gen_cfg(slurp(args.pythonfile).strip())
        g = CFGNode.to_graph(arcs)
        g.draw(args.pythonfile + '.png', prog='dot')
        print(g.string(), file=sys.stderr)
    elif args.cfg:
        cfg, first, last = get_cfg(args.pythonfile)
        for i in sorted(cfg.keys()):
            print(i, 'parents:', cfg[i]['parents'], 'children:', cfg[i]['children'])
