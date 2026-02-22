from chocopy.parser.node import (
    Type,
    TypeAnnotation,
    Program,
    ClassDefinition,
    VariableDefinition,
)
from types import ClassType, IntType, BoolType, StringType, ListType, NoneType


class BaseVisitor:
    def visit(self, node):
        if node is None:
            return None

        node_class_name = node.__class__.__name__
        method_name = f"visit_{node_class_name}"

        visitor_method = getattr(self, method_name, self.generic_visit)
        return visitor_method(node)

    def generic_visit(self, node):
        print(f"DEBUG: No special Visitor found for {type(node).__name__}")


class SemanticAnalyzer(BaseVisitor):
    def __init__(self, ast: Program):
        super().__init__()
        self.ast = ast
        self.hierarchy = {
            "object": None,
            "int": "object",
            "str": "object",
            "bool": "object",
        }
        self.globals = {}
        self.errors = []

    def analyse(self):
        self.global_discovery()

    def global_discovery(self):
        for decl in self.ast.declarations:
            if isinstance(decl, ClassDefinition):
                self.visit(decl)
        self.has_cycle()

    def visit_ClassDefinition(self, node: ClassDefinition):
        if node.name in self.hierarchy:
            self.errors.append(f"{node.name} was already defined earlier")
            return

        if node.name in ["int", "str", "bool"]:
            self.errors.append(
                f"Class {node.name} is not allowed to be named like internal types"
            )
            return

        parent = node.super_class if node.super_class else "object"
        if parent in ["int", "str", "bool"]:
            self.errors.append(f"Class {node.name} cannot inherit from internal types")
        self.hierarchy[node.name] = parent

    def has_cycle(self):
        for node in self.hierarchy:
            s = set()
            # { a: b, b: c }
            while node is not None:
                if node in s:
                    self.errors.append(f"{node} has circular dependencies")
                    break
                s.add(node)
                node = self.hierarchy.get(node)

        return

    def global_symbol_registration(self):
        self.globals["variables"] = {}
        self.globals["functions"] = {}
        self.globals["classes"] = {}

        for decl in self.ast.declarations:
            if isinstance(decl, VariableDefinition):
                self.register_variable(decl)

    def register_variable(self, node: VariableDefinition):
        name = node.var.name
        var_type = self.convert_type(node.var.type)

        if name in self.globals["variables"]:
            self.errors.append(f"Duplicate variable: {name}")
        else:
            self.globals["variable"][name] = var_type

    def convert_type(self, node: TypeAnnotation) -> Type:
        if isinstance(node, ClassType):
            if node.name == "int":
                return IntType()
            elif node.name == "bool":
                return BoolType()
            elif node.name == "str":
                return StringType()
            elif node.name == "object":
                return ClassType("object")  # Hier nutzt du dein ClassType-Objekt
            else:
                return ClassType(node.name)

        elif isinstance(node, ListType):
            inner_type = self.convert_type(node.element_type)
            return ListType(inner_type)

        return NoneType()

    def type_checking(self):
        pass
