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


class GlobalDeclaration(Node):
    def __init__(self, name: str, pos: Position):
        super().__init__(pos)
        self.name = name


class NoneLocalDeclaration(Node):
    def __init__(self, name: str, pos: Position):
        super().__init__(pos)
        self.name = name


class UnaryExpr(Expr):
    def __init__(self, operator: str, operand: Expr, pos: Position):
        super().__init__(pos)
        self.operator = operator
        self.operand = operand


class BinaryExpr(Expr):
    def __init__(self, left: Expr, operator: str, right: Expr, pos: Position):
        super().__init__(pos)
        self.left = left
        self.operator = operator
        self.right = right


class MemberExpr(Expr):
    def __init__(self, obj: Expr, member: str, pos: Position):
        super().__init__(pos)
        self.obj = obj
        self.member = member


class IndexExpr(Expr):
    def __init__(self, list_obj: Expr, index: Expr, pos: Position):
        super().__init__(pos)
        self.list_obj = list_obj
        self.index = index


class CallExpr(Expr):
    def __init__(self, function: Expr, args: list[Expr], pos: Position):
        super().__init__(pos)
        self.function = function
        self.args = args


class ListLiteral(Expr):
    def __init__(self, elements: list[Expr], pos: Position):
        super().__init__(pos)
        self.elements = elements


class VariableNode(Expr):
    def __init__(self, name: str, pos: Position):
        super().__init__(pos)
        self.name = name


class IfExpr(Expr):
    def __init__(self, node: Expr, cond: Expr, else_branch: Expr, pos: Position):
        super().__init__(pos)
        self.node = node
        self.cond = cond
        self.else_branch = else_branch


class Stmt(Node):
    pass


class Block(Node):
    def __init__(self, statements: list[Stmt], position: Position):
        super().__init__(position)
        self.statements = statements


class IfStmt(Stmt):
    def __init__(
        self,
        condition: Expr,
        then_block: list[Stmt],
        else_block: list[Stmt],
        position: Position,
    ):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block
        self.position = position


class WhileStmt(Stmt):
    def __init__(self, condition: Expr, body: list[Stmt], position: Position):
        super().__init__(position)
        self.condition = condition
        self.body = body


class ForStmt(Stmt):
    def __init__(
        self, identifier: str, iterable: Expr, body: list[Stmt], position: Position
    ):
        super().__init__(position)
        self.identifier = identifier
        self.iterable = iterable
        self.body = body


class AssignStmt(Stmt):
    def __init__(self, target: Node, value: Expr, position: Position):
        super().__init__(position)
        self.target = target
        self.value = value


class ExprStmt(Stmt):
    def __init__(self, expr: Expr, position: Position):
        super().__init__(position)
        self.expr = expr


class ReturnStmt(Stmt):
    def __init__(self, value: Expr | None, position: Position):
        super().__init__(position)
        self.value = value


class PassStmt(Stmt):
    def __init__(self, position: Position):
        super().__init__(position)


class FunctionDefinition(Node):
    def __init__(
        self,
        name: str,
        params: list[TypedVar],
        return_type: ClassType | ListType,
        var_defs: list[VariableDefinition],
        func_defs: list["FunctionDefinition"],
        statements: list[Stmt],
        position: Position,
    ):
        super().__init__(position)
        self.name = name
        self.params = params
        self.return_type = return_type
        self.var_defs = var_defs
        self.func_defs = func_defs
        self.statements = statements
