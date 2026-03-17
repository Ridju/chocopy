from chocopy.parser.node import (
    Type,
    TypeAnnotation,
    Program,
    ClassDefinition,
    VariableDefinition,
    FunctionDefinition,
    NoneLiteral,
    BoolLiteral,
    IntegerLiteral,
    StringLiteral,
    VariableNode,
    AssignStmt,
    UnaryExpr,
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

    def visit_UnaryExpr(self, node: UnaryExpr):
        operand_type = self.visit(node.operand)

        if node.operator == "-":
            if isinstance(operand_type, IntType):
                node.inferred_type = IntType()
            else:
                self.errors.append(f"Cannot apply '-' to type {operand_type}")
                node.inferred_type = IntType()
        elif node.operator == "not":
            if isinstance(operand_type, BoolType):
                node.inferred_type = BoolType()
            else:
                self.errors.append(f"Cannot apply 'not' to type {operand_type}")
                node.inferred_type = BoolType()

        return node.inferred_type

    def has_cycle(self):
        for node in self.hierarchy:
            s = set()
            while node is not None:
                if node in s:
                    self.errors.append(f"{node} has circular dependencies")
                    break
                s.add(node)
                node = self.hierarchy.get(node)

        return

    def visit_VariableNode(self, node: VariableNode):
        if node.name not in self.globals["variables"]:
            self.errors.append(f"Use of undefined vairable {node.name}")
        else:
            type = self.globals["variables"][node.name]
            node.inferred_type = type
            return type

    def visit_IntegerLiteral(self, node: IntegerLiteral):
        typ = IntType()
        node.inferred_type = typ
        return typ

    def visit_AssignStmt(self, node: AssignStmt):
        target_type = self.visit(node.target)
        value_type = self.visit(node.value)
        if not value_type.is_subtype_of(target_type, self.hierarchy):
            self.errors.append(
                f"Value of type : {value_type} is not assignable to type {target_type}"
            )

    def visit_BoolLiteral(self, node: BoolLiteral):
        typ = BoolType()
        node.inferred_type = typ
        return typ

    def visit_StringLiteral(self, node: StringLiteral):
        typ = StringType()
        node.inferred_type = typ
        return typ

    def visit_NoneLiteral(self, node: NoneLiteral):
        typ = NoneType()
        node.inferred_type = typ
        return typ

    def global_symbol_registration(self):
        self.globals["variables"] = {}
        self.globals["functions"] = {}
        self.globals["classes"] = {}

        for decl in self.ast.declarations:
            if isinstance(decl, VariableDefinition):
                self.register_variable(decl)
            if isinstance(decl, FunctionDefinition):
                self.register_function(decl)
            if isinstance(decl, ClassDefinition):
                self.register_class(decl)

    def register_class(self, node: ClassDefinition):
        name = node.name
        var_defs = {}
        method_defs = {}

        for var in node.var_defs:
            var_defs[var.name] = self.convert_type(var.var.type)

        for method in node.method_defs:
            param_types = []
            for param in method.params:
                param_types.append(self.convert_type(param.type))
            method_defs[method.name] = {
                "return_type": self.convert_type(method.return_type),
                "param_types": param_types,
            }

        if (
            node.name in self.globals["classes"]
            or node.name in self.globals["functions"]
            or node.name in self.globals["variables"]
        ):
            self.errors.append(f"Element with name: '{name}' already defined")
        else:
            self.globals["classes"][name] = {
                "variables": var_defs,
                "methods": method_defs,
            }

    def register_function(self, node: FunctionDefinition):
        name = node.name
        param_types = {}
        return_type = self.convert_type(node.return_type)
        for param in node.params:
            param_types[param.name] = self.convert_type(param.type)

        if (
            node.name in self.globals["classes"]
            or node.name in self.globals["functions"]
            or node.name in self.globals["variables"]
        ):
            self.errors.append(f"Element with name: '{name}' already defined")
        else:
            self.globals["functions"][name] = {
                "return_typ": return_type,
                "param_types": param_types,
            }

    def register_variable(self, node: VariableDefinition):
        name = node.var.name
        var_type = self.convert_type(node.var.type)

        if (
            node.name in self.globals["classes"]
            or node.name in self.globals["functions"]
            or node.name in self.globals["variables"]
        ):
            self.errors.append(f"Element with name: '{name}' already defined")
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
                return ClassType("object")
            else:
                return ClassType(node.name)

        elif isinstance(node, ListType):
            inner_type = self.convert_type(node.element_type)
            return ListType(inner_type)

        return NoneType()

    def type_checking(self):
        pass
