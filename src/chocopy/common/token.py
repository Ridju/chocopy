import enum
from dataclasses import dataclass
from typing import Any


class TokenType(enum.Enum):
    NONE = "none"
    FALSE = "false"
    TRUE = "true"
    AND = "and"
    NOT = "not"
    OR = "or"
    IS = "is"
    AS = "as"
    ASSERT = "assert"
    ASYNC = "async"
    AWAIT = "await"
    DEL = "del"
    FOR = "for"
    WHILE = "while"
    BREAK = "break"
    CONTINUE = "continue"
    CLASS = "class"
    DEF = "def"
    IF = "if"
    ELIF = "elif"
    ELSE = "else"
    EXCEPT = "except"
    FINALLY = "finally"
    FROM = "from"
    GLOBAL = "global"
    IMPORT = "import"
    IN = "in"
    LAMBDA = "lambda"
    NONLOCAL = "nonlocal"
    PASS = "pass"
    RAISE = "raise"
    RETURN = "return"
    TRY = "try"
    WITH = "with"
    YIELD = "yield"
    EOF = "eof"
    ID = "id"
    INTEGER = "integer"
    PLUS = "+"
    MINUS = "-"
    MULTIPLY = "*"
    PERCENT = "%"
    BRACKET_LEFT = "("
    BRACKET_RIGHT = ")"
    BRACE_LEFT = "["
    BRACE_RIGHT = "]"
    COMMA = ","
    DOT = "."
    COLON = ":"
    DOUBLE_SLASH = "//"
    ARROW = "->"
    LESS = "<"
    GREATER = "<"
    LESS_EQUAL = "<="
    GREATER_EQUAL = ">="
    DOUBLE_EQUAL = "=="
    EQUAL = "="
    NOT_EQUAL = "!="
    STRING = "string"


OPERATORS = {
    "+": TokenType.PLUS,
    "*": TokenType.MULTIPLY,
    "%": TokenType.PERCENT,
    "(": TokenType.BRACKET_LEFT,
    ")": TokenType.BRACKET_RIGHT,
    "[": TokenType.BRACE_LEFT,
    "]": TokenType.BRACE_RIGHT,
    ",": TokenType.COMMA,
    ":": TokenType.COLON,
    ".": TokenType.DOT,
}


KEYWORDS = {
    "None": TokenType.NONE,
    "False": TokenType.FALSE,
    "True": TokenType.TRUE,
    "and": TokenType.AND,
    "not": TokenType.NOT,
    "or": TokenType.OR,
    "is": TokenType.IS,
    "as": TokenType.AS,
    "assert": TokenType.ASSERT,
    "async": TokenType.ASYNC,
    "await": TokenType.AWAIT,
    "del": TokenType.DEL,
    "for": TokenType.FOR,
    "while": TokenType.WHILE,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "class": TokenType.CLASS,
    "def": TokenType.DEF,
    "if": TokenType.IF,
    "elif": TokenType.ELIF,
    "else": TokenType.ELSE,
    "except": TokenType.EXCEPT,
    "finally": TokenType.FINALLY,
    "from": TokenType.FROM,
    "global": TokenType.GLOBAL,
    "import": TokenType.IMPORT,
    "in": TokenType.IN,
    "lambda": TokenType.LAMBDA,
    "nonlocal": TokenType.NONLOCAL,
    "pass": TokenType.PASS,
    "raise": TokenType.RAISE,
    "return": TokenType.RETURN,
    "try": TokenType.TRY,
    "with": TokenType.WITH,
    "yield": TokenType.YIELD,
    "eof": TokenType.EOF,
}


@dataclass
class Position:
    line: int
    column: int


@dataclass
class Token:
    tokentyp: TokenType
    lexeme: str
    position: Position
    literal: Any = None
