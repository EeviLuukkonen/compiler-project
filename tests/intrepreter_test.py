from compiler.interpreter import interpret
from compiler.parser import parse
from compiler.tokenizer import tokenize

def test_interpreter() -> None:
    assert interpret(parse(tokenize('1 + 2'))) == 3
    assert interpret(parse(tokenize('if 1 > 2 then 3 else 4'))) == 4
    assert interpret(parse(tokenize('if 1 < 2 then 3 else 4'))) == 3
    assert interpret(parse(tokenize('10 + if 2 < 1 then 3 else 4'))) == 14
