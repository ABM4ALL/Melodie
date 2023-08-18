import ast
from typing import Dict, Iterator, List, Literal, Optional, Set, Tuple, Union
import pprintast

from MelodieInfra.static_analysis.base import CheckerMessage
from .base import BaseChecker, CheckerMessage, StaticCheckerRoutine


class JITClassSpecMissing(CheckerMessage):
    def __init__(self, lineno: int, jitcls_name: str, missing_attr: str) -> None:
        self.jitclass_name: str = jitcls_name
        self.missing_attr: str = missing_attr
        super().__init__("error", lineno)

    @property
    def message(self):
        return f"Attribute '{self.missing_attr}' used in jitclass '{self.jitclass_name}' is not in spec!"


class JITClassUnusedSpec(CheckerMessage):
    def __init__(self, lineno: int, jitcls_name: str, unused_attr: str) -> None:
        self.jitclass_name: str = jitcls_name
        self.unused_attr: str = unused_attr
        super().__init__("warning", lineno)

    @property
    def message(self):
        return f"Attribute '{self.unused_attr}' is unused in jitclass '{self.jitclass_name}', but defined in spec!"


class Vistor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.properties = {}
        self.funcs = set()

    def visit_Attribute(self, node: ast.Attribute):
        s = node.value
        if ast.unparse(s) == "self":
            self.properties[node.attr] = node
        return

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.funcs.add(node.name)
        for n in node.body:
            self.visit(n)


class NumbaChecker(BaseChecker):
    def __init__(self) -> None:
        self.global_variables: Optional[Dict[str, ast.AST]] = {}

    def _is_jitted_classdef(self, clsdef: ast.ClassDef) -> bool:
        return self._get_jitclass_decorator(clsdef) is not None

    def _get_jitclass_decorator(self, clsdef: ast.ClassDef) -> ast.Call:
        for deco in clsdef.decorator_list:
            if (
                isinstance(deco, ast.Call)
                and isinstance(deco.func, ast.Name)
                and deco.func.id == "jitclass"
            ):
                return deco
        return None

    def _get_jitclass_decorator_args(self, jitclass_decorator: ast.Call) -> ast.List:
        """
        Get the ast of jitclass type spec variable.
        """

        assert (
            len(jitclass_decorator.args) > 0
        ), "jitclass decorator must have at least one argument!"
        first_arg = jitclass_decorator.args[0]
        if isinstance(first_arg, ast.Name):  # Used other global variables
            assert (
                first_arg.id in self.global_variables
            ), "Jitclass Spec variable should be in the global scope!"
            var = self.global_variables[first_arg.id]
            assert isinstance(
                var, ast.List
            ), "Jitclass spec variable should be a list of (attr_name, attr_type) tuple"
            return var
        elif isinstance(first_arg, ast.List):
            return first_arg
        else:
            raise NotImplementedError(
                "Cannot recognize the declarations of jitclass spec!"
            )

    def _extract_jitclass_spec_types(self, spec_list: ast.List) -> Dict[str, ast.AST]:
        """
        Extract all type declarations from jitclass typing specification variable.
        """
        types: Dict[str, ast.AST] = {}
        attr_spec: ast.Tuple
        for attr_spec in spec_list.elts:
            assert isinstance(
                attr_spec, ast.Tuple
            ), "Jitclass spec variable should be a list of (attr_name, attr_type) tuple"
            attr_name: ast.Constant = attr_spec.elts[0]
            attr_value: Union[ast.Name, ast.Item] = attr_spec.elts[1]
            assert isinstance(
                attr_name, ast.Constant
            ), "Attribute name should be a string literal"
            types[attr_name.value] = attr_value
        return types

    def _extract_global_variables(self, module: ast.Module) -> Dict[str, ast.AST]:
        for body_item in module.body:
            if isinstance(body_item, ast.Assign):
                if len(body_item.targets) == 1:
                    assert isinstance(body_item.targets[0], ast.Name)
                    self.global_variables[body_item.targets[0].id] = body_item.value
            elif isinstance(body_item, ast.AnnAssign):
                assert isinstance(body_item.target, ast.Name)
                self.global_variables[body_item.target.id] = body_item.value

    def _extract_all_attributes(self, classdef: ast.ClassDef) -> Dict[str, ast.AST]:
        v = Vistor()
        v.visit(classdef)
        all_used_attributes = set(v.properties.keys()).difference(v.funcs)
        return {k: v.properties[k] for k in all_used_attributes}

    def check(self, ast_node: ast.Module) -> Iterator[CheckerMessage]:
        classdefs = [
            clsdef for clsdef in ast_node.body if isinstance(clsdef, ast.ClassDef)
        ]
        self._extract_global_variables(ast_node)
        # pprintast.pprintast(ast_node)
        for clsdef in [
            clsdef for clsdef in classdefs if self._is_jitted_classdef(clsdef)
        ]:
            decorator = self._get_jitclass_decorator(clsdef)
            jitspec_ast = self._get_jitclass_decorator_args(decorator)

            attr_types = self._extract_jitclass_spec_types(jitspec_ast)

            used_attrs = self._extract_all_attributes(clsdef)
            used_attrs_set = set(used_attrs.keys())
            attr_types_set = set(attr_types.keys())
            defined_unused = attr_types_set.difference(used_attrs_set)
            referenced_undefined = used_attrs_set.difference(attr_types_set)

            for undefined_varname in referenced_undefined:
                # The ast node that using the property
                property_used_at = used_attrs[undefined_varname]

                yield JITClassSpecMissing(
                    property_used_at.lineno, clsdef.name, undefined_varname
                )

            for defined_unused_varname in defined_unused:
                property_defined_at = attr_types[defined_unused_varname]
                yield JITClassUnusedSpec(
                    property_defined_at.lineno, clsdef.name, defined_unused_varname
                )


StaticCheckerRoutine.checkers.append(NumbaChecker)
