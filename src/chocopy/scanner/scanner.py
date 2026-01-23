from chocopy.common.errors import LexicalError
from chocopy.common.token import KEYWORDS, Position, Token, TokenType
from typing import Optional


class Scanner:
    def __init__(self, source: str):
        self.source = source
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1

    def scan_token(self) -> Token:
        self.skip_whitespace()

        if self.is_EOF():
            return Token(TokenType.EOF, "", Position(self.line, self.column))

        self.start = self.current

        pos = Position(self.line, self.column)
        c = self.advance()

        if c.isalpha() or c == "_":
            return self.identifier(pos)
        elif c.isdigit():
            return self.number(c, pos)
        elif c in "+":
            raise NotImplementedError("TODO")
        else:
            self.error("Unknonw token found", pos)

    def identifier(self, pos: Position) -> Token:
        while self.peek().isalnum() or self.peek() == "_":
            self.advance()

        lexeme = self.source[self.start : self.current]
        tokentyp = KEYWORDS.get(lexeme, TokenType.ID)

        literal = None
        if tokentyp == TokenType.TRUE:
            literal = True
        if tokentyp == TokenType.FALSE:
            literal = False
        if tokentyp == TokenType.NONE:
            literal = None

        return Token(tokentyp, lexeme, pos, literal)

    def number(self, c: str, pos: Position) -> Token:
        if c == "0" and self.peek().isdigit():
            self.error("Leading '0' is not allowed!", pos)

        while self.peek().isdigit():
            self.advance()

        if self.peek() == ".":
            self.error("Floats are not allowed", Position(pos.line, self.column))

        lexeme = self.source[self.start : self.current]
        literal = int(lexeme)

        if literal > (2**31 - 1):
            self.error(f"Number {lexeme} is too big", pos)

        return Token(TokenType.INTEGER, lexeme, pos, literal)

    def error(self, message: str, pos: Optional[Position] = None):
        if pos is None:
            pos = Position(self.line, self.column)
        raise LexicalError(message, pos)

    def skip_whitespace(self):
        while True:
            c = self.peek()
            if c in (" ", "\t", "\r"):
                self.advance()
            else:
                break

    def read_word(self):
        pass

    def is_EOF(self) -> bool:
        return self.current >= len(self.source)

    def peek(self) -> str:
        if self.is_EOF():
            return "\0"
        return self.source[self.current]

    def advance(self) -> str:
        c = self.source[self.current]
        self.current += 1
        if c in "\n":
            self.column = 0
            self.line += 1
        else:
            self.column += 1
        return c
