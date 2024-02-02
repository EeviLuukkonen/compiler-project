from compiler.tokenizer import tokenize, Token, L, Location

def test_tokenizer_basics() -> None:
    assert tokenize("test ") == [
        Token(type='identifier', text='test', loc=L)
    ]
    
    assert tokenize("if  3\nwhile") == [
        Token(type='identifier', text='if', loc=L),
        Token(type='int_literal', text='3', loc=L),
        Token(type='identifier', text='while', loc=L)
    ]

    assert tokenize("-3+4") == [
        Token(type='operator', text='-', loc=L),
        Token(type='int_literal', text='3', loc=L),
        Token(type='operator', text='+', loc=L),
        Token(type='int_literal', text='4', loc=L)
    ]

def test_tokenizer_punctuation() -> None:
    assert tokenize("{3 ,4;)") == [
        Token(type='punctuation', text='{', loc=L),
        Token(type='int_literal', text='3', loc=L),
        Token(type='punctuation', text=',', loc=L),
        Token(type='int_literal', text='4', loc=L),
        Token(type='punctuation', text=';', loc=L),
        Token(type='punctuation', text=')', loc=L),
    ]

    assert tokenize("2 * f(x)") == [
        Token(type='int_literal', text='2', loc=L),
        Token(type='operator', text='*', loc=L),
        Token(type='identifier', text='f', loc=L),
        Token(type='punctuation', text='(', loc=L),
        Token(type='identifier', text='x', loc=L),
        Token(type='punctuation', text=')', loc=L),
    ]    

def test_tokenizer_commments() -> None:
    assert tokenize("3x+1 # comment") == [
        Token(type='int_literal', text='3', loc=L),
        Token(type='identifier', text='x', loc=L),
        Token(type='operator', text='+', loc=L),
        Token(type='int_literal', text='1', loc=L)
    ]

def test_tokenizer_location() -> None:
    assert tokenize("jee 3 \n +") == [
        Token(type='identifier', text='jee', loc=Location(line=1, column=1)),
        Token(type='int_literal', text='3', loc=Location(line=1, column=5)),
        Token(type='operator', text='+', loc=Location(line=2, column=2))
    ]