from typing import Any
from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.type_checker import typecheck
from compiler.types import Int, Bool, SymTab, Unit, top_level_symtab

def test_type_checker() -> None:
    assert typecheck_helper('1+2') == Int
    assert typecheck_helper('1+1<2') == Bool
    assert typecheck_helper('if 1 < 2 then 3 else 4') == Int
    assert typecheck_helper('if 1 < 2 then 3 < 4 else 4 < 5') == Bool
    assert typecheck_helper('true') == Bool
    assert typecheck_helper('var x = 3') == Unit
    assert typecheck_helper('var x = 1; x') == Int
    assert typecheck_helper('var x = true; x') == Bool
    assert typecheck_helper('var y = 1; var x = y; x') == Int
    assert typecheck_helper('var x = true; x = true') == Bool
    assert typecheck_helper('var x = 1; x = x + 1') == Int
    assert typecheck_helper('1 + 2 = 3') == Int   
    assert typecheck_helper('-1') == Int
    assert typecheck_helper('1 + 2 == 3') == Int   
    assert typecheck_helper('true != false') == Bool
    assert typecheck_helper('-3 > -2') == Bool
    assert typecheck_helper('var x = -1; -x') == Int
    assert typecheck_helper('print_int(2)') == Unit
    assert typecheck_helper('print_bool(true)') == Unit
    assert typecheck_helper('1 + while true do 3 + 2') == Int

    assert_fails_typecheck('(1<2) +3')
    assert_fails_typecheck('if 1 then 3 else 4')
    assert_fails_typecheck('if 1<2 then 3 else 4<5')
    assert_fails_typecheck('var x = 1; x = 1 + true')
    assert_fails_typecheck('-true')
    assert_fails_typecheck('true == 1')
    assert_fails_typecheck('var x = 2; not x')
    assert_fails_typecheck('print_int(x, y)')
    assert_fails_typecheck('x')
    assert_fails_typecheck('print_bool(1)')

def typecheck_helper(code: str) -> Any:
    expr = parse(tokenize(code))
    symtab = SymTab(locals=dict(top_level_symtab))
    return typecheck(expr, symtab)

def assert_fails_typecheck(code: str) -> None:
    expr = parse(tokenize(code))
    symtab = SymTab(locals=dict(top_level_symtab))
    failed = False
    try:
        typecheck(expr, symtab)
    except TypeError:
        failed = True
    assert failed, f'Type-checking succeeded for {code}'