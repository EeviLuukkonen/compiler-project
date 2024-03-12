from compiler.tokenizer import tokenize, L
from compiler.parser import parse
from compiler import ast

def parser_helper(s: str) -> ast.Expression | None:
    return parse(tokenize(s)).expr

def test_parser_basics() -> None:
    assert parser_helper("1") == ast.Literal(L, 1)
    assert parser_helper('true') == ast.Literal(L, True)
    assert parser_helper("1 + 2") == ast.BinaryOp(
        left=ast.Literal(L, 1),
        op="+",
        right=ast.Literal(L, 2),
        loc=L
    )
    assert parser_helper("a + 2") == ast.BinaryOp(
        left=ast.Identifier(L, "a"),
        op="+",
        right = ast.Literal(L, 2),
        loc=L
    )
    assert parser_helper("a * 2") == ast.BinaryOp(
        left=ast.Identifier(L, "a"),
        op="*",
        right = ast.Literal(L, 2),
        loc=L
    )
    assert parser_helper("a - 2 + 3") == ast.BinaryOp(
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
    assert parser_helper("a - 2 * 3") == ast.BinaryOp(
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
    assert parser_helper("1*a - 2 * 3") == ast.BinaryOp(
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
    assert parser_helper("a - 2 % 3") == ast.BinaryOp(
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
    assert parser_helper("(a - 2) * 3") == ast.BinaryOp(
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
    assert parser_helper('1 + (2 < 3)') == ast.BinaryOp(
        left=ast.Literal(L, 1),
        op="+",
        right = ast.BinaryOp(
            left=ast.Literal(L, 2),
            op="<",
            right=ast.Literal(L, 3),
            loc=L
        ),
        loc=L
    )

def test_parser_error() -> None:
    try:
        parser_helper("a - 2 * 3 b")
        assert False
    except Exception as e:
        assert "Expected ; between expressions" in str(e)

    try:
        parser_helper("a b -")
        assert False
    except Exception as e:
        assert "Expected ; between expressions" in str(e)

    try:
        a = parser_helper("")
        print(a)
        assert False
    except Exception as e:
        assert "Empty input!" in str(e)

    try:
        parser_helper('{ a b }')
        assert False
    except Exception as e:
        assert 'expected ";"' in str(e)
    

def test_parser_comparison() -> None:
    assert parser_helper("a > 2 + 3") == ast.BinaryOp(
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
    assert parser_helper("a >= 2 + 3") == ast.BinaryOp(
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
    assert parser_helper("a == 2 < 3") == ast.BinaryOp(
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
    assert parser_helper("a < 2 != 3") == ast.BinaryOp(
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
    assert parser_helper("if a then 2") == ast.IfExpression(
        cond=ast.Identifier(L, "a"),
        then_clause=ast.Literal(L, 2),
        else_clause=None,
        loc=L
    )

    assert parser_helper("if a+2 then 2 else 3 / 4") == ast.IfExpression(
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

    assert parser_helper("0 + if a+2 then 2 else 3 / 4") == ast.BinaryOp(
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
    assert parser_helper("f(x, y + z)") == ast.FunctionCall(
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

    assert parser_helper("2 * f(x, y + z)") == ast.BinaryOp(
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

    assert parser_helper("f(g(x))") == ast.FunctionCall(
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
    assert parser_helper("2 != 3 and a") == ast.BinaryOp(
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
    assert parser_helper("2 != 3 and a and b") == ast.BinaryOp(
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

    assert parser_helper("2 != 3 or a") == ast.BinaryOp(
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

    assert parser_helper("2 and 3 or a") == ast.BinaryOp(
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
    assert parser_helper("2 or 3 and a") == ast.BinaryOp(
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
    assert parser_helper('not 3') == ast.UnaryOp(
        op='not',
        right=ast.Literal(L, 3),
        loc=L
    )
    assert parser_helper('- 3') == ast.UnaryOp(
        op='-',
        right=ast.Literal(L, 3),
        loc=L
    )  
    assert parser_helper('not not a') == ast.UnaryOp(
        op='not',
        right=ast.UnaryOp(
            op='not',
            right=ast.Identifier(L, 'a'),
            loc=L
        ),
        loc=L
    )
    assert parser_helper('not-a') == ast.UnaryOp(
        op='not',
        right=ast.UnaryOp(
            op='-',
            right=ast.Identifier(L, 'a'),
            loc=L
        ),
        loc=L
    )    

