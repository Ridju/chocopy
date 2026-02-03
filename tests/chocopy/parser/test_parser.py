import pytest
from chocopy.scanner.scanner import Scanner
from chocopy.parser.parser import Parser
from chocopy.common.token import TokenType
from chocopy.common.errors import SyntaxError


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
