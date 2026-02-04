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
