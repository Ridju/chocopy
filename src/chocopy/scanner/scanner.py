from chocopy.common.token import KEYWORDS, Position, Token, TokenType


class Scanner:
    def __init__(self, source: str):
        self.source = source
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1

    def scan_token(self):
        self.skip_whitespace()
        self.start = self.current

        token_line = self.line
        token_col = self.column

        if self.is_EOF():
            return Token(TokenType.EOF, "", Position(token_line, token_col))

        c = self.advance()

        if c.isalpha() or c == "_":
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

            return Token(tokentyp, lexeme, Position(token_line, token_col), literal)

        elif c in "+":
            raise NotImplementedError("TODO")
        else:
            raise Exception(f"[{token_line}, {token_col}]: Found unknown token")

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
