from chocopy.scanner.scanner import Scanner
from chocopy.common.token import Token, Position, TokenType
from chocopy.common.errors import SyntaxError


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
            self.consume()
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
        raise NotImplementedError

    def parse_type(self):
        raise NotImplementedError

    def parse_global_decl(self):
        raise NotImplementedError

    def parse_nonlocal_decl(self):
        raise NotImplementedError

    def parse_var_def(self):
        raise NotImplementedError

    def parse_stmt(self):
        raise NotImplementedError

    def parse_simple_stmt(self):
        raise NotImplementedError

    def parse_block(self):
        raise NotImplementedError

    def parse_literal(self):
        raise NotImplementedError

    def parse_expr(self):
        raise NotImplementedError

    def parse_cexpr(self):
        raise NotImplementedError

    def parse_bin_op(self):
        raise NotImplementedError

    def parse_member_expr(self):
        raise NotImplementedError

    def parse_index_expr(self):
        raise NotImplementedError

    def parse_target(self):
        raise NotImplementedError
