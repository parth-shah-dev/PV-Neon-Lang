# ast_nodes.py

class Program:
    def __init__(self, statements):
        self.statements = statements

# Statements
class LetStatement:
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

class PrintStatement:
    def __init__(self, expr):
        self.expr = expr

class IfStatement:
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch      # list[Statement]
        self.else_branch = else_branch      # list[Statement] or None

class WhileStatement:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body                    # list[Statement]

class ForStatement:
    def __init__(self, var_name, start_expr, end_expr, body):
        self.var_name = var_name            # string
        self.start_expr = start_expr
        self.end_expr = end_expr
        self.body = body                    # list[Statement]

class FunctionDef:
    def __init__(self, name, params, body):
        self.name = name            # string
        self.params = params        # list[str]
        self.body = body            # list[Statement]

class ReturnStatement:
    def __init__(self, expr):
        self.expr = expr            # Expression

# Expressions
class NumberLiteral:
    def __init__(self, value):
        self.value = value

class StringLiteral:
    def __init__(self, value):
        self.value = value          # Python str

class BooleanLiteral:
    def __init__(self, value):
        self.value = value          # int 0/1

class VariableRef:
    def __init__(self, name):
        self.name = name

class BinaryOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op                # "+", "-", "*", "/", "==", "!=", "<", ">", "<=", ">="
        self.right = right

class CallExpr:
    def __init__(self, name, args):
        self.name = name            # function name (str)
        self.args = args            # list[Expression]

class ArrayLiteral:
    def __init__(self, elements):
        self.elements = elements    # list[Expression]

class IndexExpr:
    def __init__(self, base, index_expr):
        self.base = base            # Expression
        self.index_expr = index_expr
