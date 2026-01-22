import pytest
from chocopy.scanner.scanner import Scanner
from chocopy.common.token import TokenType, KEYWORDS


@pytest.mark.parametrize("lexeme, expected_type", KEYWORDS.items())
def test_all_keywords(lexeme, expected_type):
    if expected_type == TokenType.EOF:
        pytest.skip("EOF is not tested via Lexem-Input")

    scanner = Scanner(lexeme)
    token = scanner.scan_token()

    assert token.tokentyp == expected_type
    assert token.lexeme == lexeme

    assert token.position.line == 1
    assert token.position.column == 1


def test_identifier_recognition():
    source = "myVariable _privateVar var123"
    scanner = Scanner(source)

    t1 = scanner.scan_token()
    assert t1.tokentyp == TokenType.ID
    assert t1.lexeme == "myVariable"

    t2 = scanner.scan_token()
    assert t2.tokentyp == TokenType.ID
    assert t2.lexeme == "_privateVar"

    t3 = scanner.scan_token()
    assert t3.tokentyp == TokenType.ID
    assert t3.lexeme == "var123"


@pytest.mark.parametrize("lexeme", KEYWORDS.keys())
def test_identifier_starts_with_keyword(lexeme):
    if lexeme == "eof":
        pytest.skip()

    append_str = "test"
    appended_lexeme = lexeme + append_str

    scanner = Scanner(appended_lexeme)
    token = scanner.scan_token()

    assert token.tokentyp == TokenType.ID
    assert token.lexeme == appended_lexeme


@pytest.mark.parametrize("lexeme", KEYWORDS.keys())
def test_identifier_ends_with_keyword(lexeme):
    if lexeme == "eof":
        pytest.skip()

    append_str = "test"
    appended_lexeme = append_str + lexeme

    scanner = Scanner(appended_lexeme)
    token = scanner.scan_token()

    assert token.tokentyp == TokenType.ID
    assert token.lexeme == appended_lexeme


@pytest.mark.parametrize("lexeme", KEYWORDS.keys())
def test_identifier_with_keyword_between(lexeme):
    if lexeme == "eof":
        pytest.skip()

    append_str = "test"
    appended_lexeme = append_str + lexeme + append_str

    scanner = Scanner(appended_lexeme)
    token = scanner.scan_token()

    assert token.tokentyp == TokenType.ID
    assert token.lexeme == appended_lexeme


@pytest.mark.parametrize("lexeme", KEYWORDS.keys())
def test_keywords_case_sensitivity(lexeme):
    if lexeme == "eof":
        pytest.skip()

    upper_lexeme = lexeme.capitalize()

    if upper_lexeme == lexeme:
        upper_lexeme = lexeme.upper()

    scanner = Scanner(upper_lexeme)
    token = scanner.scan_token()

    assert token.tokentyp == TokenType.ID
    assert token.lexeme == upper_lexeme


def test_token_sequence():
    scanner = Scanner("if while else")
    results = []

    for _ in range(3):
        results.append(scanner.scan_token().tokentyp)

    assert results == [TokenType.IF, TokenType.WHILE, TokenType.ELSE]
