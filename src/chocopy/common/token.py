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
    LABDA = "lambda"
    NONLOCAL = "nonlocal"
    PASS = "pass"
    RAISE = "raise"
    RETURN = "return"
    TRY = "try"
    WITH = "with"
    YIELD = "yield"


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
