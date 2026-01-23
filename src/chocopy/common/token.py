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
