import pytest
from chocopy.scanner.scanner import Scanner
from chocopy.parser.parser import Parser
from chocopy.common.token import TokenType
from chocopy.common.errors import SyntaxError
from chocopy.parser.node import (
    NoneLiteral,
    BoolLiteral,
    IntegerLiteral,
    StringLiteral,
    IDStringLiteral,
    ClassType,
    ListType,
    TypedVar,
    VariableDefinition,
    GlobalDeclaration,
    NoneLocalDeclaration,
    Operation,
)


@pytest.fixture
def create_parser():
    def _create(source_code: str):
        sc = Scanner(source_code)
        return Parser(sc)

    return _create


def test_peek(create_parser):
    parser = create_parser("if")
    token = parser.peek()
    assert token.tokentyp == TokenType.IF


def test_consume(create_parser):
    parser = create_parser("if True:\n    pass\n  pass")
    assert parser.current_token.tokentyp == TokenType.IF
    assert parser.next_token.tokentyp == TokenType.TRUE
    token = parser.consume()
    assert token.tokentyp == TokenType.IF
    assert parser.current_token.tokentyp == TokenType.TRUE
    assert parser.next_token.tokentyp == TokenType.COLON


def test_consume_with_new_line(create_parser):
    parser = create_parser("if True:\n    pass\n  pass")
    parser.consume()
    parser.consume()
    parser.consume()
    token = parser.consume()
    assert token.tokentyp == TokenType.NEW_LINE
    assert parser.current_token.tokentyp == TokenType.INDENT
    assert parser.next_token.tokentyp == TokenType.PASS


def test_consume_with_EOF(create_parser):
    parser = create_parser("")
    token = parser.consume()
    assert token.tokentyp == TokenType.EOF


def test_expected_pos_test(create_parser):
    parser = create_parser("if True:\n    pass\n  pass")
    assert parser.current_token.tokentyp == TokenType.IF
    assert parser.next_token.tokentyp == TokenType.TRUE
    parser.expected(TokenType.IF)
    assert parser.current_token.tokentyp == TokenType.TRUE
    assert parser.next_token.tokentyp == TokenType.COLON


def test_expected_negative_test(create_parser):
    parser = create_parser("if True:\n    pass\n  pass")
    assert parser.current_token.tokentyp == TokenType.IF
    assert parser.next_token.tokentyp == TokenType.TRUE
    with pytest.raises(SyntaxError, match="Expected"):
        parser.expected(TokenType.TRUE)


def test_check_pos_test(create_parser):
    parser = create_parser("if True:\n    pass\n  pass")
    assert parser.check(TokenType.IF)


def test_check_negative_test(create_parser):
    parser = create_parser("if")
    assert not parser.check(TokenType.TRUE)


@pytest.mark.parametrize(
    "source, nodeType, val",
    [
        ("None", NoneLiteral, None),
        ("True", BoolLiteral, True),
        ("False", BoolLiteral, False),
        ("123", IntegerLiteral, 123),
        ('"hello_world"', StringLiteral, "hello_world"),
    ],
)
def test_parse_literal(create_parser, source, nodeType, val):
    parser = create_parser(source)
    literal = parser.parse_literal()

    assert isinstance(literal, nodeType)
    assert literal.pos.line == 1
    assert literal.pos.column == 1
    assert literal.val == val


def test_parse_literal_IDString(create_parser):
    parser = create_parser("x")
    literal = parser.parse_literal()

    assert isinstance(literal, IDStringLiteral)
    assert literal.pos.line == 1
    assert literal.pos.column == 1
    assert literal.name == "x"


@pytest.mark.parametrize(
    "source, expected_val, expected_type",
    [
        ("123", 123, int),
        ("True", True, bool),
        ("False", False, bool),
        ("None", None, type(None)),
    ],
)
def test_parse_literal_value_conversion(
    create_parser, source, expected_val, expected_type
):
    parser = create_parser(source)
    node = parser.parse_literal()

    assert node.val == expected_val
    assert isinstance(node.val, expected_type)


def test_parse_string_literal_cleaning(create_parser):
    source = '"ChocoPy"'
    parser = create_parser(source)
    node = parser.parse_literal()

    assert node.val == "ChocoPy"


@pytest.mark.parametrize("source", ["+", "def", "class", "if"])
def test_parse_literal_errors(create_parser, source):
    parser = create_parser(source)

    with pytest.raises(SyntaxError, match="Expected special Literal type"):
        parser.parse_literal()


@pytest.mark.parametrize(
    "source, expected_name",
    [
        ("int", "int"),
        ("bool", "bool"),
        ("str", "str"),
        ("MyClass", "MyClass"),
    ],
)
def test_parse_class_type(create_parser, source, expected_name):
    parser = create_parser(source)
    node = parser.parse_type()
    assert node.name == expected_name


@pytest.mark.parametrize(
    "source, depth, base_name",
    [
        ("[int]", 1, "int"),
        ("[[str]]", 2, "str"),
        ("[[[MyClass]]]", 3, "MyClass"),
    ],
)
def test_parse_list_type_recursion(create_parser, source, depth, base_name):
    parser = create_parser(source)
    node = parser.parse_type()

    for _ in range(depth):
        assert isinstance(node, ListType)
        node = node.element_type

    assert isinstance(node, ClassType)
    assert node.name == base_name


@pytest.mark.parametrize(
    "source, expected_name, expected_type",
    [
        ("x: int", "x", "int"),
        ("foo: bool", "foo", "bool"),
        ("test: str", "test", "str"),
    ],
)
def test_parse_typed_var(create_parser, source, expected_name, expected_type):
    parser = create_parser(source)
    node = parser.parse_typed_var()

    assert isinstance(node, TypedVar)
    assert node.name == expected_name
    assert node.type.name == expected_type


@pytest.mark.parametrize(
    "source, expected_name, is_list",
    [
        ("x: int", "x", False),
        ("y: [int]", "y", True),
    ],
)
def test_parse_typed_var_advanced(create_parser, source, expected_name, is_list):
    parser = create_parser(source)
    node = parser.parse_typed_var()

    assert node.name == expected_name
    if is_list:
        assert isinstance(node.type, ListType)
    else:
        assert isinstance(node.type, ClassType)


def test_parse_var_def(create_parser):
    parser = create_parser("x: int = 10")
    node = parser.parse_var_def()

    assert isinstance(node, VariableDefinition)
    assert node.var.name == "x"
    assert node.var.type.name == "int"
    assert node.literal.val == 10


def test_parse_var_def_with_comment_at_end(create_parser):
    parser = create_parser("x: int = 123 #comment")
    node = parser.parse_var_def()

    assert isinstance(node, VariableDefinition)
    assert node.var.name == "x"
    assert node.var.type.name == "int"
    assert node.literal.val == 123


def test_parse_global_decl(create_parser):
    parser = create_parser("global x")
    node = parser.parse_global_decl()

    assert isinstance(node, GlobalDeclaration)
    assert node.name == "x"


def test_parse_nonlocal_decl(create_parser):
    parser = create_parser("nonlocal x")
    node = parser.parse_nonlocal_decl()

    assert isinstance(node, NoneLocalDeclaration)
    assert node.name == "x"


@pytest.mark.parametrize(
    "source, expected_name",
    [
        ("+", "+"),
        ("-", "-"),
        ("*", "*"),
        ("//", "//"),
        ("%", "%"),
        ("==", "=="),
        ("!=", "!="),
        ("<=", "<="),
        (">=", ">="),
        ("<", "<"),
        (">", ">"),
        ("is", "is"),
    ],
)
def test_parse_bin_op(create_parser, source, expected_name):
    parser = create_parser(source)
    node = parser.parse_bin_op()

    assert isinstance(node, Operation)
    assert node.name == expected_name
