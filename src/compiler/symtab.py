
from dataclasses import dataclass
from typing import Dict, Generic, Optional, TypeVar, Union
from compiler.ir import IRVar
from compiler.types import Arithmetic, Bool, Comparison, Int, Logical, PrintBool, PrintInt, ReadInt, Type, Eq

T = TypeVar('T', bound=Union[Type, IRVar])

@dataclass(frozen=True)
class SymTab(Generic[T]):
    locals: Dict[str, T]
    parent: Optional["SymTab"] = None

    def get_symbol(self, name: str) -> T:
        if name in self.locals:
            return self.locals[name]
        elif self.parent is not None:
            return self.parent.get_symbol(name)
        else:
            raise TypeError(f"Variable not found: '{name}'")
        
    def set_local(self, name: str, t: T) -> None:
        self.locals[name] = t

    def create_inner_tab(self) -> "SymTab":
        return SymTab(locals={}, parent=self)

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
    'print_bool': PrintBool,
    'read_int': ReadInt
}

root_types = {
    IRVar('+'): Arithmetic,
    IRVar('-'): Arithmetic,
    IRVar('*'): Arithmetic,
    IRVar('/'): Arithmetic,
    IRVar('<'): Comparison,
    IRVar('>'): Comparison,
    IRVar('<='): Comparison,
    IRVar('>='): Comparison,
    IRVar('=='): Eq,
    IRVar('!='): Eq,
    IRVar('unary_-'): Int,
    IRVar('unary_not'): Bool,
    IRVar('or'): Logical,
    IRVar('and'): Logical,
    IRVar('print_int'): PrintInt,
    IRVar('print_bool'): PrintBool,
    IRVar('read_int'): ReadInt
}