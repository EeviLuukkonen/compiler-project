from compiler.tokenizer import tokenize
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

    assert parse(tokenize("(a - 2) * 3")) == ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Identifier("a"),
            op="-",
            right=ast.Literal(2)
        ),
        op="*",
        right = ast.Literal(3)
    )

def test_parser_expression()-> None:
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