from typing import Any
from compiler.parser import parse
from compiler.symtab import SymTab, top_level_symtab
from compiler.tokenizer import tokenize
from compiler.type_checker import typecheck
from compiler.types import Int, Bool, Unit

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
    assert typecheck_helper('1 + 2 == 3') == Bool
    assert typecheck_helper('true != false') == Bool
    assert typecheck_helper('-3 > -2') == Bool
    assert typecheck_helper('var x = -1; -x') == Int
    assert typecheck_helper('print_int(2)') == Unit
    assert typecheck_helper('print_bool(true)') == Unit
    assert typecheck_helper('1 + while true do 3 + 2') == Int
    assert typecheck_helper('var x: Int = 2 + 1') == Unit
    assert typecheck_helper('var x: Int = 2 + 1; x') == Int
    assert typecheck_helper('var x: (Int) => Unit = print_int') == Unit
    assert typecheck_helper('{}') == Unit
    assert typecheck_helper('true or false') == Bool
    assert typecheck_helper('1<2 and 2<=2') == Bool
    assert typecheck_helper('true != false') == Bool
    assert typecheck_helper('var n: Int = read_int(); n') == Int
    assert typecheck_helper('fun square(x: Int): Unit { print_int(x * x); }') == Unit
    assert typecheck_helper('fun square(x: Int): Int { return x * x }') == Int
    assert typecheck_helper('fun square(x: Int): Int { return x * x }; square(3)') == Int
    assert typecheck_helper('fun f(x: Int): Int { return f(x-1) }') == Int
    assert typecheck_helper('while true do break') == Unit


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
    assert_fails_typecheck('while 1 do 3 + 2')
    assert_fails_typecheck('var x: Int = true')
    assert_fails_typecheck('var x: (Int) => Int = print_int')
    assert_fails_typecheck('var x: int = 3')
    assert_fails_typecheck('var x: (Int) => unit = print_int')
    assert_fails_typecheck('fun f(x: In): Unit { print_int(x * x); }')
    assert_fails_typecheck('fun f(x: Int): U { print_int(x * x); }')
    assert_fails_typecheck('fun f(): Int { return true }')
    assert_fails_typecheck('fun f(x: Int): Int { print_int(x * x); }')
    assert_fails_typecheck('fun f(n: Int): Unit { if n > 0 then { g(n-1); }}; f(3)')

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