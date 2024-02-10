from compiler.tokenizer import tokenize, L
from compiler.parser1 import parse
from compiler import ast

def test_parser_basics() -> None:
    assert parse(tokenize("1")) == ast.Literal(L, 1)

    assert parse(tokenize("1 + 2")) == ast.BinaryOp(
        left=ast.Literal(L, 1),
        op="+",
        right = ast.Literal(L, 2),
        loc=L
    )

    assert parse(tokenize("a + 2")) == ast.BinaryOp(
        left=ast.Identifier(L, "a"),
        op="+",
        right = ast.Literal(L, 2),
        loc=L
    )

    assert parse(tokenize("a * 2")) == ast.BinaryOp(
        left=ast.Identifier(L, "a"),
        op="*",
        right = ast.Literal(L, 2),
        loc=L
    )

    assert parse(tokenize("a - 2 + 3")) == ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Identifier(L, "a"),
            op="-",
            right=ast.Literal(L, 2),
            loc=L
        ),
        op="+",
        right = ast.Literal(L, 3),
        loc=L
    )

    assert parse(tokenize("a - 2 * 3")) == ast.BinaryOp(
        left=ast.Identifier(L, "a"),
        op="-",
        right=ast.BinaryOp(
            left=ast.Literal(L, 2),
            op="*",
            right=ast.Literal(L, 3),
            loc=L
        ),
        loc=L
    )

    assert parse(tokenize("1*a - 2 * 3")) == ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Literal(L, 1),
            op="*",
            right=ast.Identifier(L, "a"),
            loc=L
        ),
        op="-",
        right=ast.BinaryOp(
            left=ast.Literal(L, 2),
            op="*",
            right=ast.Literal(L, 3),
            loc=L
        ),
        loc=L
    )

    assert parse(tokenize("a - 2 % 3")) == ast.BinaryOp(
        left=ast.Identifier(L, "a"),
        op="-",
        right=ast.BinaryOp(
            left=ast.Literal(L, 2),
            op="%",
            right=ast.Literal(L, 3),
            loc=L
        ),
        loc=L
    )

    assert parse(tokenize("(a - 2) * 3")) == ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Identifier(L, "a"),
            op="-",
            right=ast.Literal(L, 2),
            loc=L
        ),
        op="*",
        right = ast.Literal(L, 3),
        loc=L
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

    try:
        parse(tokenize('{ a b }'))
        assert False
    except Exception as e:
        assert 'expected ";"' in str(e)
    

def test_parser_comparison() -> None:
    assert parse(tokenize("a > 2 + 3")) == ast.BinaryOp(
        left=ast.Identifier(L, "a"),
        op=">",
        right = ast.BinaryOp(
            left=ast.Literal(L, 2),
            op="+",
            right=ast.Literal(L, 3),
            loc=L
        ),
        loc=L
    )
    assert parse(tokenize("a >= 2 + 3")) == ast.BinaryOp(
        left=ast.Identifier(L, "a"),
        op=">=",
        right = ast.BinaryOp(
            left=ast.Literal(L, 2),
            op="+",
            right=ast.Literal(L, 3),
            loc=L
        ),
        loc=L
    )
    assert parse(tokenize("a == 2 < 3")) == ast.BinaryOp(
        left=ast.Identifier(L, "a"),
        op="==",
        right = ast.BinaryOp(
            left=ast.Literal(L, 2),
            op="<",
            right=ast.Literal(L, 3),
            loc=L
        ),
        loc=L
    )    
    assert parse(tokenize("a < 2 != 3")) == ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Identifier(L, "a"),
            op="<",
            right=ast.Literal(L, 2),
            loc=L
        ),
        op="!=",
        right=ast.Literal(L, 3),
        loc=L
    ) 

def test_parser_if() -> None:
    assert parse(tokenize("if a then 2")) == ast.IfExpression(
        cond=ast.Identifier(L, "a"),
        then_clause=ast.Literal(L, 2),
        else_clause=None,
        loc=L
    )

    assert parse(tokenize("if a+2 then 2 else 3 / 4")) == ast.IfExpression(
        cond=ast.BinaryOp(
            left=ast.Identifier(L, "a"),
            op="+",
            right=ast.Literal(L, 2),
            loc=L
        ),
        then_clause=ast.Literal(L, 2),
        else_clause=ast.BinaryOp(
            left=ast.Literal(L, 3),
            op="/",
            right=ast.Literal(L, 4),
            loc=L
        ),
        loc=L
    )

    assert parse(tokenize("0 + if a+2 then 2 else 3 / 4")) == ast.BinaryOp(
        left=ast.Literal(L, 0),
        op="+",
        right=ast.IfExpression(
            cond=ast.BinaryOp(
                left=ast.Identifier(L, "a"),
                op="+",
                right=ast.Literal(L, 2),
                loc=L
            ),
            then_clause=ast.Literal(L, 2),
            else_clause=ast.BinaryOp(
                left=ast.Literal(L, 3),
                op="/",
                right=ast.Literal(L, 4),
                loc=L
            ),
            loc=L
        ),
        loc=L
    )

def test_parser_functions() -> None:
    assert parse(tokenize("f(x, y + z)")) == ast.FunctionCall(
        call=ast.Identifier(L, 'f'),
        args=[
            ast.Identifier(L, 'x'),
            ast.BinaryOp(
                left=ast.Identifier(L, 'y'),
                op='+',
                right=ast.Identifier(L, 'z'),
                loc=L
            )
        ],
        loc=L
    )

    assert parse(tokenize("2 * f(x, y + z)")) == ast.BinaryOp(
        left=ast.Literal(L, 2),
        op="*",
        right=ast.FunctionCall(
            call=ast.Identifier(L, 'f'),
            args=[
                ast.Identifier(L, 'x'),
                ast.BinaryOp(
                    left=ast.Identifier(L, 'y'),
                    op='+',
                    right=ast.Identifier(L, 'z'),
                    loc=L
                )
            ],
            loc=L
        ),
        loc=L
    )

    assert parse(tokenize("f(g(x))")) == ast.FunctionCall(
        call=ast.Identifier(L, 'f'),
        args=[
            ast.FunctionCall(
                call=ast.Identifier(L, 'g'),
                args=[
                    ast.Identifier(L, 'x')
                ],
                loc=L
            )
        ],
        loc=L
    )

def test_parser_and_or() -> None:
    assert parse(tokenize("2 != 3 and a")) == ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Literal(L, 2),
            op='!=',
            right=ast.Literal(L, 3),
            loc=L
        ),
        op='and',
        right=ast.Identifier(L, 'a'),
        loc=L
    )
    assert parse(tokenize("2 != 3 and a and b")) == ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.BinaryOp(
                left=ast.Literal(L, 2),
                op='!=',
                right=ast.Literal(L, 3),
                loc=L
            ),
            op='and',
            right=ast.Identifier(L, 'a'),
            loc=L
        ),
        op='and',
        right=ast.Identifier(L, 'b'),
        loc=L
    )

    assert parse(tokenize("2 != 3 or a")) == ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Literal(L, 2),
            op='!=',
            right=ast.Literal(L, 3),
            loc=L
        ),
        op='or',
        right=ast.Identifier(L, 'a'),
        loc=L
    )

    assert parse(tokenize("2 and 3 or a")) == ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Literal(L, 2),
            op='and',
            right=ast.Literal(L, 3),
            loc=L
        ),
        op='or',
        right=ast.Identifier(L, 'a'),
        loc=L
    )
    assert parse(tokenize("2 or 3 and a")) == ast.BinaryOp(
        left=ast.Literal(L, 2),
        op='or',
        right=ast.BinaryOp(
            left=ast.Literal(L, 3),
            op='and',
            right=ast.Identifier(L, 'a'),
            loc=L
        ),
        loc=L
    )

def test_parser_unary() -> None:
    assert parse(tokenize('not 3')) == ast.UnaryOp(
        op='not',
        right=ast.Literal(L, 3),
        loc=L
    )
    assert parse(tokenize('- 3')) == ast.UnaryOp(
        op='-',
        right=ast.Literal(L, 3),
        loc=L
    )  
    assert parse(tokenize('not not a')) == ast.UnaryOp(
        op='not',
        right=ast.UnaryOp(
            op='not',
            right=ast.Identifier(L, 'a'),
            loc=L
        ),
        loc=L
    )
    assert parse(tokenize('not-a')) == ast.UnaryOp(
        op='not',
        right=ast.UnaryOp(
            op='-',
            right=ast.Identifier(L, 'a'),
            loc=L
        ),
        loc=L
    )    

