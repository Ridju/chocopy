import pytest
from chocopy.parser.node import *
from chocopy.semantic.chocopy_types import (
    IntType,
    StringType,
    ClassType,
)
from chocopy.semantic.analyzer import SemanticAnalyzer


def create_program(declarations=None, statements=None):
    return Program(declarations or [], statements or [])


def test_integer_literal_inference():
    node = IntegerLiteral(42)
    ast = create_program(statements=[node])
    analyzer = SemanticAnalyzer(ast)

    analyzer.visit(node)
    assert isinstance(node.inferred_type, IntType)


def test_binary_expr_addition_ints():
    left = IntegerLiteral(10)
    right = IntegerLiteral(20)
    expr = BinaryExpr(left, "+", right)

    analyzer = SemanticAnalyzer(create_program())
    analyzer.visit(expr)

    assert isinstance(expr.inferred_type, IntType)
    assert len(analyzer.errors) == 0


def test_binary_expr_type_mismatch():
    expr = BinaryExpr(IntegerLiteral(10), "+", BoolLiteral(True))

    analyzer = SemanticAnalyzer(create_program())
    analyzer.visit(expr)

    assert any("requires two ints" in err for err in analyzer.errors)


def test_undefined_variable_error():
    var_node = VariableNode("x")
    ast = create_program(statements=[var_node])
    analyzer = SemanticAnalyzer(ast)

    analyzer.visit(var_node)
    assert len(analyzer.errors) == 1
    assert "undefined variable: x" in analyzer.errors[0]


def test_global_variable_registration():
    var_def = VariableDefinition(
        VariableNode("x"), TypeAnnotation("int"), IntegerLiteral(0)
    )
    ast = create_program(declarations=[var_def])

    analyzer = SemanticAnalyzer(ast)
    analyzer.analyse()

    assert "x" in analyzer.globals["variables"]
    assert isinstance(analyzer.globals["variables"]["x"], IntType)


def test_valid_assignment():
    target = VariableNode("x")
    value = IntegerLiteral(10)
    stmt = AssignStmt(target, value)

    ast = create_program()
    analyzer = SemanticAnalyzer(ast)
    analyzer.globals["variables"]["x"] = IntType()

    analyzer.visit(stmt)
    assert len(analyzer.errors) == 0


def test_invalid_assignment_type():
    target = VariableNode("x")
    value = StringLiteral("Hello")
    stmt = AssignStmt(target, value)

    analyzer = SemanticAnalyzer(create_program())
    analyzer.globals["variables"]["x"] = IntType()

    analyzer.visit(stmt)
    assert any("not assignable" in err for err in analyzer.errors)


def test_circular_inheritance_detection():
    ast = create_program()
    analyzer = SemanticAnalyzer(ast)

    analyzer.hierarchy["A"] = "B"
    analyzer.hierarchy["B"] = "A"

    analyzer.has_cycle()
    assert any("circular dependencies" in err for err in analyzer.errors)


@pytest.mark.parametrize(
    "t1, t2, expected_common",
    [
        (IntType(), IntType(), "int"),
        (IntType(), StringType(), "object"),
        (ClassType("A"), ClassType("B"), "object"),
    ],
)
def test_get_common_ancestor(t1, t2, expected_common):
    analyzer = SemanticAnalyzer(create_program())
    common = analyzer.get_common(t1, t2)
    assert common.name == expected_common


def test_return_type_mismatch():
    ret_stmt = ReturnStmt(BoolLiteral(True))
    func = FunctionDefinition("f", [], TypeAnnotation("int"), [], [], [ret_stmt])

    analyzer = SemanticAnalyzer(create_program())
    analyzer.return_type = IntType()

    analyzer.visit(ret_stmt)
    assert any("Expected return type" in err for err in analyzer.errors)
