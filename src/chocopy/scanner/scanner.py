from chocopy.common.errors import LexicalError
from chocopy.common.token import OPERATORS, KEYWORDS, Position, Token, TokenType
from typing import Optional


class Scanner:
    def __init__(self, source: str):
        self.source = source
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        self.indent_stack = [0]
        self.token_queue = []

    def scan_token(self) -> Token:
        if self.token_queue:
            return self.token_queue.pop(0)

        self.skip_whitespace()

        if self.is_EOF():
            if len(self.indent_stack) > 1:
                self.indent_stack.pop()
                return Token(TokenType.DEDENT, "", Position(self.line, self.column))
            return Token(TokenType.EOF, "", Position(self.line, self.column))

        self.start = self.current

        pos = Position(self.line, self.column)
        c = self.advance()

        if c.isalpha() or c == "_":
            return self.identifier(pos)
        elif c.isdigit():
            return self.number(c, pos)
        elif c in "+-*/><=!()[],:.-%":
            return self.operator(c, pos)
        elif c == '"':
            return self.string(pos)
        elif c == "\n":
            return self.handle_newline(pos)
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

    def operator(self, c: str, pos: Position) -> Token:
        if c == "/":
            if self.match("/"):
                return Token(TokenType.DOUBLE_SLASH, "//", pos)
            self.error("Found unknown Operator", pos)
        elif c == "!":
            if self.match("="):
                return Token(TokenType.NOT_EQUAL, "!=", pos)
            self.error("Found unknown Operator", pos)
        elif c == "-":
            if self.match(">"):
                return Token(TokenType.ARROW, "->", pos)
            return Token(TokenType.MINUS, "-", pos)
        elif c == "<":
            if self.match("="):
                return Token(TokenType.LESS_EQUAL, "<=", pos)
            return Token(TokenType.LESS, "<", pos)
        elif c == ">":
            if self.match("="):
                return Token(TokenType.GREATER_EQUAL, ">=", pos)
            return Token(TokenType.GREATER, ">", pos)
        elif c == "=":
            if self.match("="):
                return Token(TokenType.DOUBLE_EQUAL, "==", pos)
            return Token(TokenType.EQUAL, "=", pos)
        else:
            return Token(OPERATORS[c], c, pos)

    def string(self, pos: Position) -> Token:
        result = []
        while self.peek() != '"' and not self.is_EOF():
            c = self.advance()

            if c == "\n":
                self.error("Unterminated string literal (newline not allowed)", pos)

            if c == "\\":
                if self.is_EOF():
                    break

                escape = self.advance()
                if escape == "n":
                    result.append("\n")
                elif escape == "t":
                    result.append("\t")
                elif escape == "\\":
                    result.append("\\")
                elif escape == '"':
                    result.append('"')
                else:
                    self.error(f"Invalid escape sequence: \\{escape}", pos)
            else:
                result.append(c)

        if self.is_EOF():
            self.error("Unterminated string literal", pos)

        self.advance()

        lexeme = self.source[self.start : self.current]
        literal = "".join(result)

        return Token(TokenType.STRING, lexeme, pos, literal)

    def handle_newline(self, pos: Position) -> Token:
        self.token_queue.append(Token(TokenType.NEW_LINE, "\n", pos))

        while not self.is_EOF():
            while self.peek() in (" ", "\t", "\r"):
                self.advance()

            if self.peek() == "\n":
                self.advance()
            elif self.peek() == "#":
                while self.peek() != "\n" and not self.is_EOF():
                    self.advance()
            else:
                break

        indentation = self.column - 1
        last_indent = self.indent_stack[-1]

        if indentation > last_indent:
            self.indent_stack.append(indentation)
            self.token_queue.append(
                Token(TokenType.INDENT, "", Position(self.line, self.column))
            )

        elif indentation < last_indent:
            while indentation < self.indent_stack[-1]:
                self.indent_stack.pop()
                self.token_queue.append(
                    Token(TokenType.DEDENT, "", Position(self.line, self.column))
                )

            if self.indent_stack[-1] != indentation:
                self.error(
                    "Indentation error: does not match any outer indentation level",
                    Position(self.line, self.column),
                )

        return self.token_queue.pop(0)

    def match(self, expected: str) -> bool:
        if self.peek() == expected:
            self.advance()
            return True
        return False

    def expected(self, c: str) -> bool:
        return self.peek() == c

    def error(self, message: str, pos: Optional[Position] = None):
        if pos is None:
            pos = Position(self.line, self.column)
        raise LexicalError(message, pos)

    def skip_whitespace_except_newline(self):
        while self.peek() in (" ", "\t", "\r"):
            self.advance()

    def skip_whitespace(self):
        while True:
            c = self.peek()
            if c in (" ", "\t", "\r"):
                self.advance()
            elif c == "#":
                while self.peek() != "\n" and not self.is_EOF():
                    self.advance()
            else:
                break

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
