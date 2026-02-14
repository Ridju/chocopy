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


class TypeAnnotation(Node):
    def __init__(self, pos: Position):
        super().__init__(pos)


class ClassType(TypeAnnotation):
    def __init__(self, name: str, pos: Position):
        super().__init__(pos)
        self.name = name


class ListType(TypeAnnotation):
    def __init__(self, el: TypeAnnotation, pos: Position):
        super().__init__(pos)
        self.element_type = el


class TypedVar(Node):
    def __init__(self, name: str, type: TypeAnnotation, pos: Position):
        super().__init__(pos)
        self.name = name
        self.type = type


class VariableDefinition(Node):
    def __init__(
        self,
        var: TypedVar,
        literal: Literal,
    ):
        super().__init__(var.pos)
        self.var = var
        self.literal = literal
