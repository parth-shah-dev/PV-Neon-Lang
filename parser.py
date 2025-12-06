# parser.py

from ast_nodes import (
    Program,
    LetStatement,
    PrintStatement,
    IfStatement,
    WhileStatement,
    ForStatement,
    FunctionDef,
    ReturnStatement,
    NumberLiteral,
    StringLiteral,
    BooleanLiteral,
    VariableRef,
    BinaryOp,
    CallExpr,
    ArrayLiteral,
    IndexExpr,
)
from lexer import TT_NUMBER, TT_STRING, TT_IDENT, TT_KEYWORD, TT_SYMBOL, TT_EOF

class ParserError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        if self.pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.pos]

    def peek(self):
        nxt = self.pos + 1
        if nxt >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[nxt]

    def expect(self, type_=None, value=None, msg="Unexpected token"):
        tok = self.current()
        if (type_ is not None and tok.type != type_) or (value is not None and tok.value != value):
            raise ParserError(f"{msg} at line {tok.line}, col {tok.col}. Got {tok.type}({tok.value})")
        self.pos += 1
        return tok

    def parse(self):
        statements = []
        while self.current().type != TT_EOF:
            statements.append(self.parse_statement())
        return Program(statements)

    def parse_statement(self):
        tok = self.current()

        # fun definition
        if tok.type == TT_KEYWORD and tok.value == "fun":
            return self.parse_function_def()

        # let statement
        if tok.type == TT_KEYWORD and tok.value == "let":
            return self.parse_let()


        # print statement
        if tok.type == TT_KEYWORD and tok.value == "print":
            return self.parse_print()

        # if statement
        if tok.type == TT_KEYWORD and tok.value == "if":
            return self.parse_if()

        # while statement
        if tok.type == TT_KEYWORD and tok.value == "while":
            return self.parse_while()

        # for statement: for i in 0 to 10 { ... }
        if tok.type == TT_KEYWORD and tok.value == "for":
            return self.parse_for()

        # return statement
        if tok.type == TT_KEYWORD and tok.value == "return":
            return self.parse_return()

        raise ParserError(f"Unknown statement at line {tok.line}, col {tok.col}")

    # fun name(a, b, ...) { ... }
    def parse_function_def(self):
        self.expect(TT_KEYWORD, "fun", "Expected 'fun'")
        name_tok = self.expect(TT_IDENT, msg="Expected function name after 'fun'")
        self.expect(TT_SYMBOL, "(", "Expected '(' after function name")

        params = []
        if not (self.current().type == TT_SYMBOL and self.current().value == ")"):
            while True:
                param_tok = self.expect(TT_IDENT, msg="Expected parameter name")
                params.append(param_tok.value)
                if self.current().type == TT_SYMBOL and self.current().value == ",":
                    self.pos += 1
                    continue
                break

        self.expect(TT_SYMBOL, ")", "Expected ')' after parameter list")
        body = self.parse_block()
        return FunctionDef(name_tok.value, params, body)

    # let IDENT = expr ;
    def parse_let(self):
        self.expect(TT_KEYWORD, "let", "Expected 'let'")
        name_tok = self.expect(TT_IDENT, msg="Expected identifier after 'let'")
        self.expect(TT_SYMBOL, "=", "Expected '=' after identifier")
        expr = self.parse_expression()
        self.expect(TT_SYMBOL, ";", "Expected ';' at end of let statement")
        return LetStatement(name_tok.value, expr)

    # print ( expr ) ;
    def parse_print(self):
        self.expect(TT_KEYWORD, "print", "Expected 'print'")
        self.expect(TT_SYMBOL, "(", "Expected '(' after 'print'")
        expr = self.parse_expression()
        self.expect(TT_SYMBOL, ")", "Expected ')' after expression")
        self.expect(TT_SYMBOL, ";", "Expected ';' after print statement")
        return PrintStatement(expr)

    # return expr ;
    def parse_return(self):
        self.expect(TT_KEYWORD, "return", "Expected 'return'")
        expr = self.parse_expression()
        self.expect(TT_SYMBOL, ";", "Expected ';' after return")
        return ReturnStatement(expr)

    # if (cond) { ... } else { ... }
    def parse_if(self):
        self.expect(TT_KEYWORD, "if", "Expected 'if'")
        self.expect(TT_SYMBOL, "(", "Expected '(' after 'if'")
        condition = self.parse_expression()
        self.expect(TT_SYMBOL, ")", "Expected ')' after condition")
        then_branch = self.parse_block()

        else_branch = None
        if self.current().type == TT_KEYWORD and self.current().value == "else":
            self.pos += 1  # consume 'else'
            else_branch = self.parse_block()

        return IfStatement(condition, then_branch, else_branch)

    # while (cond) { ... }
    def parse_while(self):
        self.expect(TT_KEYWORD, "while", "Expected 'while'")
        self.expect(TT_SYMBOL, "(", "Expected '(' after 'while'")
        condition = self.parse_expression()
        self.expect(TT_SYMBOL, ")", "Expected ')' after condition")
        body = self.parse_block()
        return WhileStatement(condition, body)

    # for i in start to end { ... }
    def parse_for(self):
        self.expect(TT_KEYWORD, "for", "Expected 'for'")
        name_tok = self.expect(TT_IDENT, msg="Expected loop variable name")
        self.expect(TT_KEYWORD, "in", "Expected 'in' after for variable")
        start_expr = self.parse_expression()
        self.expect(TT_KEYWORD, "to", "Expected 'to' after start expression")
        end_expr = self.parse_expression()
        body = self.parse_block()
        return ForStatement(name_tok.value, start_expr, end_expr, body)

    # { stmt* }
    def parse_block(self):
        self.expect(TT_SYMBOL, "{", "Expected '{' to start block")
        statements = []
        while not (self.current().type == TT_SYMBOL and self.current().value == "}"):
            if self.current().type == TT_EOF:
                raise ParserError("Unexpected end of file inside block")
            statements.append(self.parse_statement())
        self.expect(TT_SYMBOL, "}", "Expected '}' to end block")
        return statements

    # Expression grammar:
    # expr         -> equality
    # equality     -> comparison ( ( "==" | "!=" ) comparison )*
    # comparison   -> term ( ( "<" | ">" | "<=" | ">=" ) term )*
    # term         -> factor ( ( "+" | "-" ) factor )*
    # factor       -> unary ( ( "*" | "/" ) unary )*
    # unary        -> postfix
    # postfix      -> primary ( "[" expr "]" )*
    # primary      -> NUMBER | STRING | BOOLEAN | IDENT | IDENT "(" args ")" | array | "(" expr ")"
    # array        -> "[" (expr ("," expr)*)? "]"

    def parse_expression(self):
        return self.parse_equality()

    def parse_equality(self):
        node = self.parse_comparison()
        while self.current().type == TT_SYMBOL and self.current().value in ("==", "!="):
            op_tok = self.current()
            self.pos += 1
            right = self.parse_comparison()
            node = BinaryOp(node, op_tok.value, right)
        return node

    def parse_comparison(self):
        node = self.parse_term()
        while self.current().type == TT_SYMBOL and self.current().value in ("<", ">", "<=", ">="):
            op_tok = self.current()
            self.pos += 1
            right = self.parse_term()
            node = BinaryOp(node, op_tok.value, right)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.current().type == TT_SYMBOL and self.current().value in ("+", "-"):
            op_tok = self.current()
            self.pos += 1
            right = self.parse_factor()
            node = BinaryOp(node, op_tok.value, right)
        return node

    def parse_factor(self):
        node = self.parse_unary()
        while self.current().type == TT_SYMBOL and self.current().value in ("*", "/"):
            op_tok = self.current()
            self.pos += 1
            right = self.parse_unary()
            node = BinaryOp(node, op_tok.value, right)
        return node

    def parse_unary(self):
        # you can add unary ops later; for now directly postfix
        return self.parse_postfix()

    def parse_postfix(self):
        node = self.parse_primary()
        # index: arr[expr]
        while self.current().type == TT_SYMBOL and self.current().value == "[":
            self.pos += 1  # skip [
            index_expr = self.parse_expression()
            self.expect(TT_SYMBOL, "]", "Expected ']' after index expression")
            node = IndexExpr(node, index_expr)
        return node

    def parse_primary(self):
        tok = self.current()

        if tok.type == TT_NUMBER:
            self.pos += 1
            return NumberLiteral(tok.value)

        if tok.type == TT_STRING:
            self.pos += 1
            return StringLiteral(tok.value)

        if tok.type == TT_KEYWORD and tok.value in ("true", "false"):
            self.pos += 1
            return BooleanLiteral(1 if tok.value == "true" else 0)

        # array literal
        if tok.type == TT_SYMBOL and tok.value == "[":
            return self.parse_array_literal()

        if tok.type == TT_IDENT:
            ident_tok = tok
            next_tok = self.peek()
            # function call
            if next_tok.type == TT_SYMBOL and next_tok.value == "(":
                self.pos += 2  # IDENT + "("
                args = []
                if not (self.current().type == TT_SYMBOL and self.current().value == ")"):
                    while True:
                        arg_expr = self.parse_expression()
                        args.append(arg_expr)
                        if self.current().type == TT_SYMBOL and self.current().value == ",":
                            self.pos += 1
                            continue
                        break
                self.expect(TT_SYMBOL, ")", "Expected ')' after arguments")
                return CallExpr(ident_tok.value, args)
            # variable ref
            self.pos += 1
            return VariableRef(ident_tok.value)

        if tok.type == TT_SYMBOL and tok.value == "(":
            self.pos += 1
            expr = self.parse_expression()
            self.expect(TT_SYMBOL, ")", "Expected ')'")
            return expr

        raise ParserError(f"Unexpected token {tok.type}({tok.value}) at line {tok.line}, col {tok.col}")

    def parse_array_literal(self):
        self.expect(TT_SYMBOL, "[", "Expected '[' for array literal")
        elements = []
        if not (self.current().type == TT_SYMBOL and self.current().value == "]"):
            while True:
                elements.append(self.parse_expression())
                if self.current().type == TT_SYMBOL and self.current().value == ",":
                    self.pos += 1
                    continue
                break
        self.expect(TT_SYMBOL, "]", "Expected ']' at end of array literal")
        return ArrayLiteral(elements)
