from chocopy.scanner.scanner import Scanner
from chocopy.common.token import Token, Position, TokenType
from chocopy.common.errors import SyntaxError
from chocopy.parser.node import (
    Literal,
    IDStringLiteral,
    StringLiteral,
    IntegerLiteral,
    BoolLiteral,
    NoneLiteral,
    ClassType,
    ListType,
    TypedVar,
    VariableDefinition,
    GlobalDeclaration,
    NoneLocalDeclaration,
    VariableNode,
    UnaryExpr,
    BinaryExpr,
    IfExpr,
    MemberExpr,
    IndexExpr,
    CallExpr,
    ListLiteral,
)


class Parser:
    def __init__(self, sc: Scanner):
        self.sc = sc
        self.current_token = self.sc.scan_token()
        self.next_token = self.sc.scan_token()

    def parse(self):
        raise NotImplementedError

    def peek(self) -> Token:
        return self.current_token

    def consume(self) -> Token:
        curr = self.current_token
        self.current_token = self.next_token
        self.next_token = self.sc.scan_token()
        return curr

    def expected(self, type: TokenType):
        if self.check(type):
            return self.consume()
        else:
            self.error(
                f"Expected {type} but got {self.peek().tokentyp}",
                self.peek().position,
            )

    def error(self, msg: str, pos: Position):
        raise SyntaxError(msg, pos)

    def check(self, type: TokenType):
        return self.peek().tokentyp == type

    def parse_programm(self):
        raise NotImplementedError

    def parse_class_def(self):
        raise NotImplementedError

    def parse_class_body(self):
        raise NotImplementedError

    def parse_func_def(self):
        raise NotImplementedError

    def parse_func_body(self):
        raise NotImplementedError

    def parse_typed_var(self):
        token = self.peek()
        if token.tokentyp == TokenType.ID:
            id = self.consume()
            _ = self.expected(TokenType.COLON)
            type = self.parse_type()

            return TypedVar(id.lexeme, type, id.position)
        else:
            self.error(
                f"Expected variable identifier, found {token.tokentyp}", token.position
            )

    def parse_type(self):
        token = self.peek()
        if token.tokentyp == TokenType.ID:
            self.consume()
            return ClassType(token.lexeme, token.position)
        elif token.tokentyp == TokenType.BRACE_LEFT:
            self.consume()
            el = self.parse_type()
            self.expected(TokenType.BRACE_RIGHT)
            return ListType(el, token.position)
        else:
            self.error(
                f"Expected variable type, found {token.tokentyp}", token.position
            )

    def parse_global_decl(self):
        token = self.peek()
        if token.tokentyp == TokenType.GLOBAL:
            self.consume()
            id = self.expected(TokenType.ID)
            if self.peek().tokentyp != TokenType.EOF:
                self.expected(TokenType.NEW_LINE)

            return GlobalDeclaration(id.lexeme, id.position)
        else:
            self.error(
                f"Expected 'global' keyword, found {token.tokentyp}", token.position
            )

    def parse_nonlocal_decl(self):
        token = self.peek()
        if token.tokentyp == TokenType.NONLOCAL:
            self.consume()
            id = self.expected(TokenType.ID)
            if self.peek().tokentyp != TokenType.EOF:
                self.expected(TokenType.NEW_LINE)

            return NoneLocalDeclaration(id.lexeme, id.position)
        else:
            self.error(
                f"Expected 'nonlocal' keyword, found {token.tokentyp}", token.position
            )

    def parse_var_def(self):
        var = self.parse_typed_var()
        self.expected(TokenType.EQUAL)
        literal = self.parse_literal()
        if self.peek().tokentyp != TokenType.EOF:
            self.expected(TokenType.NEW_LINE)
        return VariableDefinition(var, literal)

    def parse_stmt(self):
        raise NotImplementedError

    def parse_simple_stmt(self):
        raise NotImplementedError

    def parse_block(self):
        raise NotImplementedError

    def parse_literal(self) -> Literal:
        token = self.peek()
        if token.tokentyp == TokenType.NONE:
            self.consume()
            return NoneLiteral(token)
        elif token.tokentyp == TokenType.TRUE:
            self.consume()
            return BoolLiteral(token)
        elif token.tokentyp == TokenType.FALSE:
            self.consume()
            return BoolLiteral(token)
        elif token.tokentyp == TokenType.INTEGER:
            self.consume()
            return IntegerLiteral(token)
        elif token.tokentyp == TokenType.ID:
            self.consume()
            return IDStringLiteral(token)
        elif token.tokentyp == TokenType.STRING:
            self.consume()
            return StringLiteral(token)
        else:
            self.error(
                f"Expected special Literal type, found {token.tokentyp}", token.position
            )

    def parse_expr(self):
        node = self.parse_or_expr()
        if self.peek().tokentyp == TokenType.IF:
            self.consume()
            cond = self.parse_or_expr()
            self.expected(TokenType.ELSE)
            else_branch = self.parse_expr()
            return IfExpr(node, cond, else_branch)
        return node

    def parse_primary(self):
        node = None
        token = self.peek()
        if token.tokentyp in [
            TokenType.INTEGER,
            TokenType.STRING,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.NONE,
        ]:
            node = self.parse_literal()
        elif token.tokentyp == TokenType.ID:
            self.consume()
            node = VariableNode(token.lexeme, token.position)
        elif token.tokentyp == TokenType.BRACKET_LEFT:
            self.consume()
            expr = self.parse_expr()
            self.expected(TokenType.BRACKET_RIGHT)
            node = expr
        elif token.tokentyp == TokenType.BRACE_LEFT:
            self.consume()
            expressions = []
            if not self.check(TokenType.BRACE_RIGHT):
                expressions.append(self.parse_expr())
            while self.check(TokenType.COMMA):
                self.consume()
                expressions.append(self.parse_expr())
            self.expected(TokenType.BRACE_RIGHT)
            node = ListLiteral(expressions, token.position)
        else:
            self.error(f"Expected cexpr found {token.tokentyp}", token.position)

        while True:
            if self.peek().tokentyp == TokenType.DOT:
                self.consume()
                id = self.expected(TokenType.ID)
                node = self.parse_member_expr(node, id)
            elif self.peek().tokentyp == TokenType.BRACE_LEFT:
                self.consume()
                expr = self.parse_expr()
                self.expected(TokenType.BRACE_RIGHT)
                node = IndexExpr(node, expr)
            elif self.peek().tokentyp == TokenType.BRACKET_LEFT:
                self.consume()
                args = []
                if not self.check(TokenType.BRACKET_RIGHT):
                    args.append(self.parse_expr())
                while self.check(TokenType.COMMA):
                    self.consume()
                    args.append(self.parse_expr())
                self.expected(TokenType.BRACKET_RIGHT)
                node = CallExpr(node, args)
            else:
                break

        return node

    def parse_unary(self):
        token = self.peek()
        if token.tokentyp == TokenType.MINUS or token.tokentyp == TokenType.NOT:
            operator = self.consume()
            return UnaryExpr(operator.lexeme, self.parse_unary(), token.position)
        else:
            return self.parse_primary()

    def parse_term(self):
        left = self.parse_unary()
        while self.peek().tokentyp in [
            TokenType.MULTIPLY,
            TokenType.DOUBLE_SLASH,
            TokenType.PERCENT,
        ]:
            op = self.consume()
            right = self.parse_unary()
            left = BinaryExpr(left, op.lexeme, right, op.position)

        return left

    def parse_arithmetic(self):
        left = self.parse_term()
        while self.peek().tokentyp in [TokenType.PLUS, TokenType.MINUS]:
            op = self.consume()
            right = self.parse_term()
            left = BinaryExpr(left, op.lexeme, right, op.position)

        return left

    def parse_comparison(self):
        left = self.parse_arithmetic()
        while self.peek().tokentyp in [
            TokenType.DOUBLE_EQUAL,
            TokenType.NOT_EQUAL,
            TokenType.LESS,
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS_EQUAL,
            TokenType.IS,
        ]:
            op = self.consume()
            right = self.parse_arithmetic()
            left = BinaryExpr(left, op.lexeme, right, op.position)

        return left

    def parse_and_expr(self):
        left = self.parse_comparison()
        while self.peek().tokentyp == TokenType.AND:
            op = self.consume()
            right = self.parse_comparison()
            left = BinaryExpr(left, op.lexeme, right, op.position)

        return left

    def parse_or_expr(self):
        left = self.parse_and_expr()
        while self.peek().tokentyp == TokenType.OR:
            op = self.consume()
            right = self.parse_and_expr()
            left = BinaryExpr(left, op.lexeme, right, op.position)

        return left

    def parse_target(self):
        raise NotImplementedError
