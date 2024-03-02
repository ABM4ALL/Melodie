# -*- coding:utf-8 -*-
# @Time: 2022/12/13 21:54
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: test_ast.py


#
# def test_ast_manipulator():
#     if sys.version_info.major == 3 and sys.version_info.minor <= 7:
#         return
#     am = FuncDefManipulator(os.path.join(
#         os.path.dirname(__file__), 'demo.py'), 'setup')
#
#     am.add_record("self.add_agent_property", ('agents', 'id_xxxxxxx'))
#     am.remove_record("self.add_agent_property", ('agents', 'cash'))
#     am.remove_record("self.add_agent_property", ('agents', 'fine'))
#     unparsed = astunparse.unparse(am.root)
#
#     assert " " * 8 + \
#         "self.add_agent_property('agents', 'id_xxxxxxx')" in unparsed
#     assert " " * 8 + \
#         "self.add_agent_property('agents', 'cash')" not in unparsed
#     assert " " * 8 + \
#         "self.add_agent_property('agents', 'fine')" not in unparsed
#
#     # ast parse the generated code to make sure no syntax error exists.
#     ast.parse(unparsed)
#
#     print(astunparse.unparse(am.root))
#
#
# def test_model_parser():
#     model_ast = get_model_ast(CovidModel)
#     # pprintast.pprintast(model_ast)
#     walk_model_ast(model_ast, sys.modules[CovidModel.__module__].__file__)
