from chocopy.common.token import Token, Position


class Node:
    def __init__(self, pos: Position):
        self.pos = pos


class Expr(Node):
    def __init__(self, pos: Position):
        super().__init__(pos)


class Literal(Expr):
    def __init__(self, token: Token):
        self.val = token.literal
        super().__init__(token.position)


class NoneLiteral(Literal):
    def __init__(self, token: Token):
        super().__init__(token)


class BoolLiteral(Literal):
    def __init__(self, token: Token):
        super().__init__(token)


class IntegerLiteral(Literal):
    def __init__(self, token: Token):
        super().__init__(token)


class StringLiteral(Literal):
    def __init__(self, token: Token):
        super().__init__(token)


class IDStringLiteral(Expr):
    def __init__(self, token: Token):
        self.name = token.lexeme
        super().__init__(token.position)
