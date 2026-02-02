from scanner import Scanner
from common import Token


class Parser:
    def __init__(self, sc: Scanner):
        self.sc = sc
        self.current_token = None
        self.next_token = None

    def parse(self):
        raise NotImplementedError

    def peek(self) -> Token:
        raise NotImplementedError

    def consume(self) -> Token:
        raise NotImplementedError

    def expected(self, token: Token):
        raise NotImplementedError

    def check(self, token: Token):
        raise NotImplementedError

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
