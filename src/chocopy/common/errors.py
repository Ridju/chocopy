from chocopy.common.token import Position


class ChocoPyError(Exception):
    def __init__(self, message: str, pos: Position):
        self.message = message
        self.pos = pos
        super().__init__(f"[{pos.line}, {pos.column}]: {message}")


class LexicalError(ChocoPyError):
    pass


class SyntaxError(ChocoPyError):
    pass


class SemanticError(ChocoPyError):
    pass
