class Scanner:
    def __init__(self, source: str):
        self.source = source
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1

    def scan_token(self):
        pass

    def is_EOF(self) -> bool:
        return self.current >= len(self.source)

    def peek(self) -> str:
        if self.is_EOF():
            return "\0"
        return self.source[self.current]

    def advance(self) -> str:
        char = self.source[self.current]
        self.current += 1
        if char in "\n":
            self.column = 0
            self.line += 1
        else:
            self.column += 1
        return char
