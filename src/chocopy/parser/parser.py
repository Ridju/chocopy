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
    IfStmt,
    WhileStmt,
    ForStmt,
    PassStmt,
    AssignStmt,
    ExprStmt,
    ReturnStmt,
    FunctionDefinition,
    ClassDefinition,
    Program,
)


class Parser:
    def __init__(self, sc: Scanner):
        self.sc = sc
        self.current_token = self.sc.scan_token()
        self.next_token = self.sc.scan_token()

    def parse(self) -> Program:
        return self.parse_programm()

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
        pos = self.peek().position
        declarations = []
        stmts = []

        while self.peek().tokentyp == TokenType.CLASS:
            declarations.append(self.parse_class_def())

        while (
            self.peek().tokentyp == tokentyp.ID
            and self.next_token.tokentyp == TokenType.COLON
        ):
            declarations.append(self.parse_var_def())

        while self.peek().tokentyp == TokenType.DEF:
            declarations.append(self.parse_func_def())

        while self.peek().tokentyp != TokenType.EOF:
            if self.peek().tokentyp == TokenType.NEW_LINE:
                self.consume()
                continue
            stmts.append(self.parse_stmt())

        return Program(declarations, stmts, pos)

    def parse_class_def(self):
        class_token = self.consume()
        name = self.expected(TokenType.ID)

        self.expected(TokenType.BRACKET_LEFT)
        super_name = self.expected(TokenType.ID)
        self.expected(TokenType.BRACKET_RIGHT)

        self.expected(TokenType.COLON)

        var_defs, method_defs = self.parse_class_body()

        return ClassDefinition(
            name.lexeme, super_name.lexeme, var_defs, method_defs, class_token.position
        )

    def parse_class_body(self):
        self.expected(TokenType.NEW_LINE)
        self.expected(TokenType.INDENT)

        var_defs = []
        method_defs = []

        if self.peek().tokentyp == TokenType.PASS:
            self.consume()
            self.expected(TokenType.NEW_LINE)
        else:
            while (
                self.peek().tokentyp == TokenType.ID
                and self.next_token.tokentyp == TokenType.COLON
            ):
                var_defs.append(self.parse_var_def())
            while self.peek().tokentyp == TokenType.DEF:
                method_defs.append(self.parse_func_def())

        self.expected(TokenType.DEDENT)
        return var_defs, method_defs

    def parse_func_def(self):
        def_token = self.consume()
        id = self.expected(TokenType.ID)
        self.expected(TokenType.BRACKET_LEFT)
        params = []
        if self.peek().tokentyp != TokenType.BRACKET_RIGHT:
            params.append(self.parse_typed_var())
            while self.peek().tokentyp != TokenType.BRACKET_RIGHT:
                self.expected(TokenType.COMMA)
                params.append(self.parse_typed_var())
        self.expected(TokenType.BRACKET_RIGHT)
        self.expected(TokenType.ARROW)
        return_type = self.parse_type()
        self.expected(TokenType.COLON)
        var_defs, func_defs, stmt_defs = self.parse_func_body()

        return FunctionDefinition(
            id.lexeme,
            params,
            return_type,
            var_defs,
            func_defs,
            stmt_defs,
            def_token.position,
        )

    def parse_func_body(self):
        self.expected(TokenType.NEW_LINE)
        indent_token = self.expected(TokenType.INDENT)

        var_defs = []
        func_defs = []
        stmt_defs = []

        while True:
            token = self.peek()
            if (
                token.tokentyp == TokenType.ID
                and self.next_token.tokentyp == TokenType.COLON
            ):
                var_defs.append(self.parse_var_def())
            elif token.tokentyp == TokenType.GLOBAL:
                var_defs.append(self.parse_global_decl())
            elif token.tokentyp == TokenType.NONLOCAL:
                var_defs.append(self.parse_nonlocal_decl())
            else:
                break

        while self.peek().tokentyp == TokenType.DEF:
            func_defs.append(self.parse_func_def())

        while self.peek().tokentyp != TokenType.DEDENT:
            if self.peek().tokentyp == TokenType.NEW_LINE:
                self.consume()
                continue
            stmt_defs.append(self.parse_stmt())

        self.expected(TokenType.DEDENT)
        return var_defs, func_defs, stmt_defs

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
        token = self.peek()
        if token.tokentyp == TokenType.IF:
            return self.parse_if_stmt()
        elif token.tokentyp == TokenType.WHILE:
            return self.parse_while_stmt()
        elif token.tokentyp == TokenType.FOR:
            return self.parse_for_stmt()
        else:
            return self.parse_simple_stmt()

    def parse_if_stmt(self):
        if_token = self.consume()
        cond = self.parse_expr()
        self.expected(TokenType.COLON)
        then_block = self.parse_block()

        else_block = []

        if self.peek().tokentyp == TokenType.ELIF:
            else_block.append(self.parse_if_stmt())
        elif self.peek().tokentyp == TokenType.ELSE:
            self.consume()
            self.expected(TokenType.COLON)
            else_block = self.parse_block()

        return IfStmt(cond, then_block, else_block, if_token.position)

    def parse_while_stmt(self):
        while_token = self.consume()
        while_cond = self.parse_expr()
        self.expected(TokenType.COLON)
        return WhileStmt(while_cond, self.parse_block(), while_token.position)

    def parse_for_stmt(self):
        for_token = self.consume()
        id = self.expected(TokenType.ID)
        self.expected(TokenType.IN)
        iterable = self.parse_expr()
        self.expected(TokenType.COLON)
        body = self.parse_block()
        return ForStmt(id.lexeme, iterable, body, for_token.position)

    def parse_simple_stmt(self):
        token = self.peek()
        node = None
        if token.tokentyp == TokenType.PASS:
            self.consume()
            node = PassStmt(token.position)
        elif token.tokentyp == TokenType.RETURN:
            return_token = self.consume()
            val = None
            if self.peek().tokentyp not in [
                TokenType.NEW_LINE,
                TokenType.DEDENT,
                TokenType.EOF,
            ]:
                val = self.parse_expr()
            node = ReturnStmt(val, return_token.position)
        else:
            left = self.parse_expr()
            if self.peek().tokentyp == TokenType.EQUAL:
                equal_token = self.consume()
                if not isinstance(left, (VariableNode, MemberExpr, IndexExpr)):
                    self.error(
                        f"cannot assign to {left.__class__.__name__} at x",
                        equal_token.position,
                    )
                right = self.parse_expr()
                node = AssignStmt(left, right, equal_token.position)
            else:
                node = ExprStmt(left, token.position)

        if self.peek().tokentyp == TokenType.NEW_LINE:
            self.consume()
        elif self.peek().tokentyp not in [TokenType.EOF, TokenType.DEDENT]:
            self.error(
                f"Exepcted newline after statement, found {self.peek().tokentyp}",
                self.peek().position,
            )

        return node

    def parse_block(self):
        self.expected(TokenType.NEW_LINE)
        token = self.expected(TokenType.INDENT)
        stmts = []
        while self.peek().tokentyp != TokenType.DEDENT:
            if self.peek().tokentyp == TokenType.NEW_LINE:
                self.consume()
                continue
            stmts.append(self.parse_stmt())

        if len(stmts) == 0:
            self.error(f"Empty blocks are not allowed", token.position)

        self.expected(TokenType.DEDENT)
        return stmts

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
            token = self.consume()
            cond = self.parse_or_expr()
            self.expected(TokenType.ELSE)
            else_branch = self.parse_expr()
            return IfExpr(node, cond, else_branch, token.position)
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
            curr_token = self.peek()
            if curr_token.tokentyp == TokenType.DOT:
                self.consume()
                member = self.expected(TokenType.ID)
                node = MemberExpr(
                    node,
                    VariableNode(member.lexeme, member.position),
                    curr_token.position,
                )
            elif curr_token.tokentyp == TokenType.BRACE_LEFT:
                self.consume()
                expr = self.parse_expr()
                self.expected(TokenType.BRACE_RIGHT)
                node = IndexExpr(node, expr, curr_token.position)
            elif curr_token.tokentyp == TokenType.BRACKET_LEFT:
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
