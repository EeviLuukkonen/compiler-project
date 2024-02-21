
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass(frozen=True)
class Type:
    '''Base class for types'''

@dataclass(frozen=True)
class BasicType(Type):
    name: str

@dataclass(frozen=True)
class FunType(Type):
    parameters: list[Type]
    return_type: Type

@dataclass(frozen=True)
class SymTab():
    locals: Dict[str, Type]
    parent: Optional["SymTab"] = None

    def get_type(self, name: str) -> Type:
        if name in self.locals:
            return self.locals[name]
        elif self.parent is not None:
            return self.parent.get_type(name)
        else:
            raise TypeError(f"Variable not found: '{name}'")
        
    def set_type(self, name: str, type: Type) -> None:
        self.locals[name] = type

    def create_inner_tab(self) -> "SymTab":
        return SymTab(locals={}, parent=self)

Int = BasicType('Int')
Bool = BasicType('Bool')
Unit = BasicType('Unit')
Arithmetic = FunType([Int, Int], Int)
Comparison = FunType([Int, Int], Bool)
Logical = FunType([Bool, Bool], Bool)
PrintInt = FunType([Int], Unit)
PrintBool = FunType([Bool], Unit)

top_level_symtab = {
        '+': Arithmetic,
        '-': Arithmetic,
        '*': Arithmetic,
        '/': Arithmetic,
        '<': Comparison,
        '>': Comparison,
        '<=': Comparison,
        '>=': Comparison,
        'unary_-': Int,
        'unary_not': Bool,
        'or': Logical,
        'and': Logical,
        'print_int': PrintInt,
        'print_bool': PrintBool
    }