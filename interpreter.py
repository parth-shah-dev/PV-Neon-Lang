# interpreter.py

import math
import random

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

class RuntimeErrorPV(Exception):
    pass

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class Interpreter:
    def __init__(self):
        self.env = {}          # current variables (globals / locals)
        self.functions = {}    # name -> FunctionDef

    def run(self, program: Program):
        for stmt in program.statements:
            self.execute_statement(stmt)

    def execute_statement(self, stmt):
        if isinstance(stmt, LetStatement):
            value = self.evaluate_expression(stmt.expr)
            self.env[stmt.name] = value

        elif isinstance(stmt, PrintStatement):
            value = self.evaluate_expression(stmt.expr)
            print(value)

        elif isinstance(stmt, IfStatement):
            cond_val = self.evaluate_expression(stmt.condition)
            if self.is_truthy(cond_val):
                for s in stmt.then_branch:
                    self.execute_statement(s)
            elif stmt.else_branch is not None:
                for s in stmt.else_branch:
                    self.execute_statement(s)

        elif isinstance(stmt, WhileStatement):
            while self.is_truthy(self.evaluate_expression(stmt.condition)):
                for s in stmt.body:
                    self.execute_statement(s)

        elif isinstance(stmt, ForStatement):
            start_val = self.evaluate_expression(stmt.start_expr)
            end_val = self.evaluate_expression(stmt.end_expr)
            if not isinstance(start_val, int) or not isinstance(end_val, int):
                raise RuntimeErrorPV("for loop bounds must be integers")
            i = start_val
            while i <= end_val:
                self.env[stmt.var_name] = i
                for s in stmt.body:
                    self.execute_statement(s)
                i += 1

        elif isinstance(stmt, FunctionDef):
            self.functions[stmt.name] = stmt

        elif isinstance(stmt, ReturnStatement):
            value = self.evaluate_expression(stmt.expr)
            raise ReturnException(value)

        else:
            raise RuntimeErrorPV(f"Unknown statement type: {type(stmt)}")

    def is_truthy(self, value):
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return value != ""
        if isinstance(value, list):
            return len(value) != 0
        return bool(value)

    def evaluate_expression(self, expr):
        if isinstance(expr, NumberLiteral):
            return expr.value

        if isinstance(expr, StringLiteral):
            return expr.value

        if isinstance(expr, BooleanLiteral):
            return expr.value

        if isinstance(expr, VariableRef):
            if expr.name not in self.env:
                raise RuntimeErrorPV(f"Undefined variable '{expr.name}'")
            return self.env[expr.name]

        if isinstance(expr, ArrayLiteral):
            return [self.evaluate_expression(e) for e in expr.elements]

        if isinstance(expr, IndexExpr):
            base_val = self.evaluate_expression(expr.base)
            index_val = self.evaluate_expression(expr.index_expr)
            if not isinstance(index_val, int):
                raise RuntimeErrorPV("Index must be integer")
            try:
                return base_val[index_val]
            except Exception:
                raise RuntimeErrorPV("Index out of range")

        if isinstance(expr, BinaryOp):
            left_val = self.evaluate_expression(expr.left)
            right_val = self.evaluate_expression(expr.right)
            op = expr.op

            # string concat
            if op == "+" and (isinstance(left_val, str) or isinstance(right_val, str)):
                return str(left_val) + str(right_val)

            # numeric ops
            if op in {"+", "-", "*", "/"}:
                if not isinstance(left_val, int) or not isinstance(right_val, int):
                    raise RuntimeErrorPV(f"Operator {op} requires integers")
                if op == "+":
                    return left_val + right_val
                if op == "-":
                    return left_val - right_val
                if op == "*":
                    return left_val * right_val
                if op == "/":
                    if right_val == 0:
                        raise RuntimeErrorPV("Division by zero")
                    return left_val // right_val

            # comparisons: allow ints or strings
            if op in {"==", "!=", "<", ">", "<=", ">="}:
                if type(left_val) != type(right_val):
                    raise RuntimeErrorPV("Comparison requires same types")
                if op == "==":
                    return 1 if left_val == right_val else 0
                if op == "!=":
                    return 1 if left_val != right_val else 0
                if op == "<":
                    return 1 if left_val < right_val else 0
                if op == ">":
                    return 1 if left_val > right_val else 0
                if op == "<=":
                    return 1 if left_val <= right_val else 0
                if op == ">=":
                    return 1 if left_val >= right_val else 0

            raise RuntimeErrorPV(f"Unknown operator {op}")

        if isinstance(expr, CallExpr):
            return self.call_function(expr.name, expr.args)

        raise RuntimeErrorPV(f"Unknown expression type: {type(expr)}")

    def call_function(self, name, arg_exprs):
        # built-ins first
        if name == "len":
            if len(arg_exprs) != 1:
                raise RuntimeErrorPV("len() expects 1 argument")
            val = self.evaluate_expression(arg_exprs[0])
            if isinstance(val, (str, list)):
                return len(val)
            raise RuntimeErrorPV("len() expects string or array")

        if name == "sqrt":
            if len(arg_exprs) != 1:
                raise RuntimeErrorPV("sqrt() expects 1 argument")
            val = self.evaluate_expression(arg_exprs[0])
            if not isinstance(val, int):
                raise RuntimeErrorPV("sqrt() expects integer")
            return int(math.isqrt(val))

        if name == "random":
            if len(arg_exprs) == 1:
                max_val = self.evaluate_expression(arg_exprs[0])
                if not isinstance(max_val, int):
                    raise RuntimeErrorPV("random(max) expects integer")
                return random.randint(0, max_val)
            elif len(arg_exprs) == 2:
                a = self.evaluate_expression(arg_exprs[0])
                b = self.evaluate_expression(arg_exprs[1])
                if not isinstance(a, int) or not isinstance(b, int):
                    raise RuntimeErrorPV("random(a,b) expects integers")
                return random.randint(a, b)
            else:
                raise RuntimeErrorPV("random() expects 1 or 2 arguments")

        if name == "input":
            prompt = ""
            if len(arg_exprs) == 1:
                prompt = str(self.evaluate_expression(arg_exprs[0]))
            elif len(arg_exprs) > 1:
                raise RuntimeErrorPV("input() expects 0 or 1 argument")
            return input(prompt)

        # user-defined functions
        if name not in self.functions:
            raise RuntimeErrorPV(f"Undefined function '{name}'")

        func_def = self.functions[name]

        if len(arg_exprs) != len(func_def.params):
            raise RuntimeErrorPV(
                f"Function '{name}' expected {len(func_def.params)} args, got {len(arg_exprs)}"
            )

        arg_values = [self.evaluate_expression(arg) for arg in arg_exprs]

        old_env = self.env
        new_env = {}
        for param_name, value in zip(func_def.params, arg_values):
            new_env[param_name] = value

        self.env = new_env

        result = 0
        try:
            for stmt in func_def.body:
                self.execute_statement(stmt)
        except ReturnException as r:
            result = r.value
        finally:
            self.env = old_env

        return result
