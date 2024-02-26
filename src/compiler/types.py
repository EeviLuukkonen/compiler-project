
from dataclasses import dataclass

@dataclass
class Type:
    '''Base class for types'''

@dataclass
class BasicType(Type):
    name: str

    def __repr__(self) -> str:
        return self.name

@dataclass
class FunType(Type):
    parameters: list[Type]
    return_type: Type

Int = BasicType('Int')
Bool = BasicType('Bool')
Unit = BasicType('Unit')
Arithmetic = FunType([Int, Int], Int)
Comparison = FunType([Int, Int], Bool)
Logical = FunType([Bool, Bool], Bool)
PrintInt = FunType([Int], Unit)
PrintBool = FunType([Bool], Unit)
