
from compiler import ast
from dataclasses import dataclass

@dataclass
class Type:
    '''Base class for types'''

@dataclass
class BasicType(Type):
    name: str

    def __repr__(self) -> str:
        return self.name
    
    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, BasicType) and self.name == other.name
        ) or (
            isinstance(other, ast.BasicTypeExpr) and self.name == other.name
        )

@dataclass
class FunType(Type):
    parameters: list[Type]
    return_type: Type

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, FunType)
            and self.parameters == other.parameters
            and self.return_type == other.return_type
        ) or (
            isinstance(other, ast.FunTypeExpr)
            and self.parameters == other.parameters
            and self.return_type == other.return_type
        )

@dataclass
class EqType(Type):
    '''Class for equality and inequality'''

Int = BasicType('Int')
Bool = BasicType('Bool')
Unit = BasicType('Unit')
Arithmetic = FunType([Int, Int], Int)
Comparison = FunType([Int, Int], Bool)
Logical = FunType([Bool, Bool], Bool)
PrintInt = FunType([Int], Unit)
PrintBool = FunType([Bool], Unit)
ReadInt = FunType([], Int)
Eq = EqType()
