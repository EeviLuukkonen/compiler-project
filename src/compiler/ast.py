from dataclasses import dataclass
from compiler.tokenizer import Location

@dataclass
class Expression:
    "base class for expression ast nodes"
    loc: Location

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class Literal(Expression):
    value: int | bool | None

@dataclass
class BinaryOp(Expression):
    left: Expression | None
    op: str
    right: Expression

@dataclass
class IfExpression(Expression):
    cond: Expression
    then_clause: Expression
    else_clause: Expression | None

@dataclass
class FunctionCall(Expression):
    call: Identifier
    args: list[Expression]

@dataclass
class UnaryOp(Expression):
    op: str
    right: Expression

@dataclass
class Block(Expression):
    expressions: list[Expression]

@dataclass
class VariableDec(Expression):
    variable: Identifier
    value: Expression