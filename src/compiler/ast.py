from dataclasses import dataclass, field
from compiler.tokenizer import Location
from compiler import types

@dataclass
class Expression:
    "base class for expression ast nodes"
    loc: Location
    type: types.Type = field(kw_only=True, default_factory=lambda: types.Unit)

@dataclass
class TypeExpr:
    "base class for expression types"

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class Literal(Expression):
    value: int | bool | None

@dataclass
class BinaryOp(Expression):
    left: Expression
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
    expressions: list[Expression] | None

@dataclass
class VariableDec(Expression):
    variable: Identifier
    value: Expression
    var_type: TypeExpr | None

@dataclass
class WhileLoop(Expression):
    cond: Expression
    do: Expression

@dataclass
class BasicTypeExpr(TypeExpr):
    name: str

    def __repr__(self) -> str:
        return self.name
    
    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, BasicTypeExpr) and self.name == other.name
        ) or (
            isinstance(other, types.BasicType) and self.name == other.name
        )

@dataclass
class FunTypeExpr(TypeExpr):
    parameters: list[TypeExpr]
    return_type: TypeExpr

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, FunTypeExpr)
            and self.parameters == other.parameters
            and self.return_type == other.return_type
        ) or (
            isinstance(other, types.FunType)
            and self.parameters == other.parameters
            and self.return_type == other.return_type
        )

Int = BasicTypeExpr('Int')
Bool = BasicTypeExpr('Bool')
Unit = BasicTypeExpr('Unit')