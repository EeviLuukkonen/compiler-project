import pytest
from compiler.tokenizer import tokenize, Location
from compiler.parser1 import parse
from compiler import ast

def test_parser_basics() -> None:
    assert parse(tokenize("1")) == ast.Literal(1)

    assert parse(tokenize("1 + 2")) == ast.BinaryOp(
        left=ast.Literal(1),
        op="+",
        right = ast.Literal(2)
    )

    assert parse(tokenize("a + 2")) == ast.BinaryOp(
        left=ast.Identifier("a"),
        op="+",
        right = ast.Literal(2)
    )

    assert parse(tokenize("a * 2")) == ast.BinaryOp(
        left=ast.Identifier("a"),
        op="*",
        right = ast.Literal(2)
    )

    assert parse(tokenize("a - 2 + 3")) == ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Identifier("a"),
            op="-",
            right=ast.Literal(2)
        ),
        op="+",
        right = ast.Literal(3)
    )

    assert parse(tokenize("a - 2 * 3")) == ast.BinaryOp(
        left=ast.Identifier("a"),
        op="-",
        right=ast.BinaryOp(
            left=ast.Literal(2),
            op="*",
            right=ast.Literal(3)
        )
    )

    assert parse(tokenize("1*a - 2 * 3")) == ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Literal(1),
            op="*",
            right=ast.Identifier("a")
        ),
        op="-",
        right=ast.BinaryOp(
            left=ast.Literal(2),
            op="*",
            right=ast.Literal(3)
        )
    )

    assert parse(tokenize("a - 2 % 3")) == ast.BinaryOp(
        left=ast.Identifier("a"),
        op="-",
        right=ast.BinaryOp(
            left=ast.Literal(2),
            op="%",
            right=ast.Literal(3)
        )
    )

    assert parse(tokenize("(a - 2) * 3")) == ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Identifier("a"),
            op="-",
            right=ast.Literal(2)
        ),
        op="*",
        right = ast.Literal(3)
    )

def test_parser_error() -> None:
    try:
        parse(tokenize("a - 2 * 3 b"))
        assert False
    except Exception as e:
        assert "Unknown syntax at the end of the code:" in str(e)

    try:
        parse(tokenize("a b -"))
        assert False
    except Exception as e:
        assert "Unknown syntax at the end of the code:" in str(e)

    try:
        parse(tokenize(""))
        assert False
    except Exception as e:
        assert "Empty input!" in str(e)
    

def test_parser_comparison() -> None:
    assert parse(tokenize("a > 2 + 3")) == ast.BinaryOp(
        left=ast.Identifier("a"),
        op=">",
        right = ast.BinaryOp(
            left=ast.Literal(2),
            op="+",
            right=ast.Literal(3)
        )
    )
    assert parse(tokenize("a >= 2 + 3")) == ast.BinaryOp(
        left=ast.Identifier("a"),
        op=">=",
        right = ast.BinaryOp(
            left=ast.Literal(2),
            op="+",
            right=ast.Literal(3)
        )
    )
    assert parse(tokenize("a == 2 < 3")) == ast.BinaryOp(
        left=ast.Identifier("a"),
        op="==",
        right = ast.BinaryOp(
            left=ast.Literal(2),
            op="<",
            right=ast.Literal(3)
        )
    )    
    assert parse(tokenize("a < 2 != 3")) == ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Identifier("a"),
            op="<",
            right=ast.Literal(2)
        ),
        op="!=",
        right=ast.Literal(3)
    ) 

def test_parser_if() -> None:
    assert parse(tokenize("if a then 2")) == ast.IfExpression(
        cond=ast.Identifier("a"),
        then_clause=ast.Literal(2),
        else_clause=None
    )

    assert parse(tokenize("if a+2 then 2 else 3 / 4")) == ast.IfExpression(
        cond=ast.BinaryOp(
            left=ast.Identifier("a"),
            op="+",
            right=ast.Literal(2)
        ),
        then_clause=ast.Literal(2),
        else_clause=ast.BinaryOp(
            left=ast.Literal(3),
            op="/",
            right=ast.Literal(4)
        )
    )

    assert parse(tokenize("0 + if a+2 then 2 else 3 / 4")) == ast.BinaryOp(
        left=ast.Literal(0),
        op="+",
        right=ast.IfExpression(
            cond=ast.BinaryOp(
                left=ast.Identifier("a"),
                op="+",
                right=ast.Literal(2)
            ),
            then_clause=ast.Literal(2),
            else_clause=ast.BinaryOp(
                left=ast.Literal(3),
                op="/",
                right=ast.Literal(4)
            )
        )
    )

def test_parser_functions() -> None:
    assert parse(tokenize("f(x, y + z)")) == ast.FunctionCall(
        call=ast.Identifier('f'),
        args=[
            ast.Identifier('x'),
            ast.BinaryOp(
                left=ast.Identifier('y'),
                op='+',
                right=ast.Identifier('z')
            )
        ]
    )

    assert parse(tokenize("2 * f(x, y + z)")) == ast.BinaryOp(
        left=ast.Literal(2),
        op="*",
        right=ast.FunctionCall(
            call=ast.Identifier('f'),
            args=[
                ast.Identifier('x'),
                ast.BinaryOp(
                    left=ast.Identifier('y'),
                    op='+',
                    right=ast.Identifier('z')
                )
            ]
        )
    )

    assert parse(tokenize("f(g(x))")) == ast.FunctionCall(
        call=ast.Identifier('f'),
        args=[
            ast.FunctionCall(
                call=ast.Identifier('g'),
                args=[
                    ast.Identifier('x')
                ]
            )
        ]
    )

def test_parser_and_or() -> None:
    assert parse(tokenize("2 != 3 and a")) == ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Literal(2),
            op='!=',
            right=ast.Literal(3)
        ),
        op='and',
        right=ast.Identifier('a')
    )
    assert parse(tokenize("2 != 3 and a and b")) == ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.BinaryOp(
                left=ast.Literal(2),
                op='!=',
                right=ast.Literal(3)
            ),
            op='and',
            right=ast.Identifier('a')
        ),
        op='and',
        right=ast.Identifier('b')
    )

    assert parse(tokenize("2 != 3 or a")) == ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Literal(2),
            op='!=',
            right=ast.Literal(3)
        ),
        op='or',
        right=ast.Identifier('a')
    )

    assert parse(tokenize("2 and 3 or a")) == ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Literal(2),
            op='and',
            right=ast.Literal(3)
        ),
        op='or',
        right=ast.Identifier('a')
    )
    assert parse(tokenize("2 or 3 and a")) == ast.BinaryOp(
        left=ast.Literal(2),
        op='or',
        right=ast.BinaryOp(
            left=ast.Literal(3),
            op='and',
            right=ast.Identifier('a')
        )
    )

def test_parser_unary() -> None:
    assert parse(tokenize('not 3')) == ast.UnaryOp(
        op='not',
        right=ast.Literal(3)
    )
    assert parse(tokenize('- 3')) == ast.UnaryOp(
        op='-',
        right=ast.Literal(3)
    )  
    assert parse(tokenize('not not a')) == ast.UnaryOp(
        op='not',
        right=ast.UnaryOp(
            op='not',
            right=ast.Identifier('a')
        )
    )
    assert parse(tokenize('not-a')) == ast.UnaryOp(
        op='not',
        right=ast.UnaryOp(
            op='-',
            right=ast.Identifier('a')
        )
    )    

def test_parser_expression() -> None:
    assert parse(tokenize("if 2 or 3 and a then jee + 1")) == ast.IfExpression(
        cond=ast.BinaryOp(
            left=ast.Literal(2),
            op='or',
            right=ast.BinaryOp(
                left=ast.Literal(3),
                op='and',
                right=ast.Identifier('a')
            )
        ),
        then_clause=ast.BinaryOp(
            left=ast.Identifier('jee'),
            op='+',
            right=ast.Literal(1)
        ),
        else_clause=None
    )
    assert parse(tokenize('if not not a then (1 + 2)')) == ast.IfExpression(
        cond=ast.UnaryOp(
            op='not',
            right=ast.UnaryOp(
                op='not',
                right=ast.Identifier('a')
            )
        ),
        then_clause=ast.BinaryOp(
            left=ast.Literal(1),
            op='+',
            right=ast.Literal(2)
        ),
        else_clause=None
    )
    assert parse(tokenize('1+2 = 3')) == ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Literal(1),
            op='+',
            right=ast.Literal(2)
        ),
        op='=',
        right=ast.Literal(3)
    )
    assert parse(tokenize('2 = 1 = 3')) == ast.BinaryOp(
        left=ast.Literal(2),
        op='=',
        right=ast.BinaryOp(
            left=ast.Literal(1),
            op='=',
            right=ast.Literal(3)
        )
    )
    assert parse(tokenize('if 2 = 1+1 then -3')) == ast.IfExpression(
        cond=ast.BinaryOp(
            left=ast.Literal(2),
            op='=',
            right=ast.BinaryOp(
                left=ast.Literal(1),
                op='+',
                right=ast.Literal(1)
            ),
        ),
        then_clause=ast.UnaryOp(
            op='-',
            right=ast.Literal(3)
        ),
        else_clause=None
    )

def test_parser_block() -> None:
    assert parse(tokenize('''
        {
            f(a);
            x = y;
            f(x)
        }
        ''')) == ast.Block(
            statements=[
                ast.FunctionCall(
                    call=ast.Identifier('f'),
                    args=[ast.Identifier('a')]
                ),
                ast.BinaryOp(
                    left=ast.Identifier('x'),
                    op='=',
                    right=ast.Identifier('y')
                ),
                ast.FunctionCall(
                    call=ast.Identifier('f'),
                    args=[ast.Identifier('x')]
                )
            ]
        )
    
    assert parse(tokenize('''
        {
            f(a);
            x = y;
            f(x);
        }
        ''')) == ast.Block(
            statements=[
                ast.FunctionCall(
                    call=ast.Identifier('f'),
                    args=[ast.Identifier('a')]
                ),
                ast.BinaryOp(
                    left=ast.Identifier('x'),
                    op='=',
                    right=ast.Identifier('y')
                ),
                ast.FunctionCall(
                    call=ast.Identifier('f'),
                    args=[ast.Identifier('x')]
                ),
                ast.Literal(None)
            ]
        )

    try:
        parse(tokenize('''
            {
                f(a)
                x = y;
                f(x)
            }
        '''))
        assert False
    except Exception as e:
        assert 'expected ";"' in str(e)
