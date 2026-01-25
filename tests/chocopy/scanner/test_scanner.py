import pytest
from chocopy.common.errors import LexicalError
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
        token = scanner.scan_token()
        results.append((token.tokentyp, token.position.line, token.position.column))

    assert results == [
        (TokenType.IF, 1, 1),
        (TokenType.WHILE, 1, 4),
        (TokenType.ELSE, 1, 10),
    ]


def test_EOF_token():
    scanner = Scanner("")

    for _ in range(0, 10):
        token = scanner.scan_token()
        assert token.tokentyp == TokenType.EOF


def test_zero_number():
    scanner = Scanner("0")
    token = scanner.scan_token()

    assert token.tokentyp == TokenType.INTEGER
    assert token.literal == 0
    assert token.lexeme == "0"


def test_true_literal():
    scanner = Scanner("True")
    token = scanner.scan_token()

    assert token.literal == True


def test_false_literal():
    scanner = Scanner("False")
    token = scanner.scan_token()

    assert token.literal == False


def test_None_literal():
    scanner = Scanner("None")
    token = scanner.scan_token()

    assert token.literal == None


def test_leading_zero():
    scanner = Scanner("0123")

    with pytest.raises(LexicalError, match="Leading '0'"):
        scanner.scan_token()


def test_number():
    scanner = Scanner("123")
    token = scanner.scan_token()

    assert token.tokentyp == TokenType.INTEGER
    assert token.lexeme == "123"
    assert token.literal == 123


def test_number_too_big():
    scanner = Scanner("2147483648")
    with pytest.raises(LexicalError, match="Number 2147483648"):
        scanner.scan_token()


def test_float_number():
    scanner = Scanner("123.123")
    with pytest.raises(LexicalError, match="Floats are not"):
        scanner.scan_token()


@pytest.mark.parametrize(
    "lexeme, expected_type",
    [
        ("+", TokenType.PLUS),
        ("-", TokenType.MINUS),
        ("*", TokenType.MULTIPLY),
        ("//", TokenType.DOUBLE_SLASH),
        ("%", TokenType.PERCENT),
        ("<", TokenType.LESS),
        (">", TokenType.GREATER),
        ("<=", TokenType.LESS_EQUAL),
        (">=", TokenType.GREATER_EQUAL),
        ("==", TokenType.DOUBLE_EQUAL),
        ("!=", TokenType.NOT_EQUAL),
        ("=", TokenType.EQUAL),
        ("(", TokenType.BRACKET_LEFT),
        (")", TokenType.BRACKET_RIGHT),
        ("[", TokenType.BRACE_LEFT),
        ("]", TokenType.BRACE_RIGHT),
        (",", TokenType.COMMA),
        (":", TokenType.COLON),
        (".", TokenType.DOT),
        ("->", TokenType.ARROW),
    ],
)
def test_all_operators(lexeme, expected_type):
    scanner = Scanner(lexeme)
    token = scanner.scan_token()

    assert token.tokentyp == expected_type
    assert token.lexeme == lexeme

    assert token.position.line == 1
    assert token.position.column == 1


@pytest.mark.parametrize("lexeme", ["/", "!"])
def test_single_slash_or_exclamation_mark(lexeme):
    scanner = Scanner(lexeme)

    with pytest.raises(LexicalError, match="Found unknown"):
        scanner.scan_token()
