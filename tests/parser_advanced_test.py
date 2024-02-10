from compiler.tokenizer import tokenize, L, Location
from compiler.parser1 import parse
from compiler import ast

def test_parser_expression() -> None:
    assert parse(tokenize("if 2 or 3 and a then jee + 1")) == ast.IfExpression(
        cond=ast.BinaryOp(
            left=ast.Literal(L, 2),
            op='or',
            right=ast.BinaryOp(
                left=ast.Literal(L, 3),
                op='and',
                right=ast.Identifier(L, 'a'),
                loc=L
            ),
            loc=L
        ),
        then_clause=ast.BinaryOp(
            left=ast.Identifier(L, 'jee'),
            op='+',
            right=ast.Literal(L, 1),
            loc=L
        ),
        else_clause=None,
        loc=L
    )
    assert parse(tokenize('if not not a then (1 + 2)')) == ast.IfExpression(
        cond=ast.UnaryOp(
            op='not',
            right=ast.UnaryOp(
                op='not',
                right=ast.Identifier(L, 'a'),
                loc=L
            ),
            loc=L
        ),
        then_clause=ast.BinaryOp(
            left=ast.Literal(L, 1),
            op='+',
            right=ast.Literal(L, 2),
            loc=L
        ),
        else_clause=None,
        loc=L
    )
    assert parse(tokenize('1+2 = 3')) == ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Literal(L, 1),
            op='+',
            right=ast.Literal(L, 2),
            loc=L
        ),
        op='=',
        right=ast.Literal(L, 3),
        loc=L
    )
    assert parse(tokenize('2 = 1 = 3')) == ast.BinaryOp(
        left=ast.Literal(L, 2),
        op='=',
        right=ast.BinaryOp(
            left=ast.Literal(L, 1),
            op='=',
            right=ast.Literal(L, 3),
            loc=L
        ),
        loc=L
    )
    assert parse(tokenize('if 2 = 1+1 then -3')) == ast.IfExpression(
        cond=ast.BinaryOp(
            left=ast.Literal(L, 2),
            op='=',
            right=ast.BinaryOp(
                left=ast.Literal(L, 1),
                op='+',
                right=ast.Literal(L, 1),
                loc=L
            ),
            loc=L
        ),
        then_clause=ast.UnaryOp(
            op='-',
            right=ast.Literal(L, 3),
            loc=L
        ),
        else_clause=None,
        loc=L
    )

def test_parser_block() -> None:
    assert parse(tokenize('''
        {
            f(a);
            x = y;
            f(x)
        };
        ''')) == ast.Block(
            expressions=[
                ast.FunctionCall(
                    call=ast.Identifier(L, 'f'),
                    args=[ast.Identifier(L, 'a')],
                    loc=L
                ),
                ast.BinaryOp(
                    left=ast.Identifier(L, 'x'),
                    op='=',
                    right=ast.Identifier(L, 'y'),
                    loc=L
                ),
                ast.FunctionCall(
                    call=ast.Identifier(L, 'f'),
                    args=[ast.Identifier(L, 'x')],
                    loc=L
                )
            ],
            loc=L
        )
    
    assert parse(tokenize('''
        {
            f(a);
            x = y;
            f(x);
        };
        ''')) == ast.Block(
            expressions=[
                ast.FunctionCall(
                    call=ast.Identifier(L, 'f'),
                    args=[ast.Identifier(L, 'a')],
                    loc=L
                ),
                ast.BinaryOp(
                    left=ast.Identifier(L, 'x'),
                    op='=',
                    right=ast.Identifier(L, 'y'),
                    loc=L
                ),
                ast.FunctionCall(
                    call=ast.Identifier(L, 'f'),
                    args=[ast.Identifier(L, 'x')],
                    loc=L
                ),
                ast.Literal(L, None)
            ],
            loc=L
        )

    try:
        parse(tokenize('''
            {
                f(a)
                x = y;
                f(x)
            };
        '''))
        assert False
    except Exception as e:
        assert 'expected ";"' in str(e)

    try:
        parse(tokenize('''
            {
                f(a);
                x = y;;
                f(x)
            };
        '''))
        assert False
    except Exception as e:
        assert 'Unknown syntax at' in str(e)

    assert parse(tokenize('if {a}; then {b};')) == ast.IfExpression(
        cond=ast.Block(
            expressions=[ast.Identifier(L, 'a')],
            loc=L
        ),
        then_clause=ast.Block(
            expressions=[ast.Identifier(L, 'b')],
            loc=L
        ),
        else_clause=None,
        loc=L
    )
    assert parse(tokenize('{ ja }')) == ast.Block(
        expressions=[
            ast.Identifier(L, 'ja')
        ],
        loc=L
    )
    assert parse(tokenize('{ 3 + { eka } { toka } }')) == ast.Block(
        expressions=[
            ast.BinaryOp(
                left=ast.Literal(L, 3),
                op='+',
                right=ast.Block(
                    expressions=[ast.Identifier(L, 'eka')],
                    loc=L
                    ),
                loc=L
            ),
            ast.Block(
                expressions=[ast.Identifier(L, 'toka')],
                loc=L
            )
        ],
        loc=L
    )
    assert parse(tokenize('{ if true then { a } b; c }')) == ast.Block(
        expressions=[
            ast.IfExpression(
                cond=ast.Identifier(L, 'true'),
                then_clause=ast.Block(
                    expressions=[ast.Identifier(L, 'a')],
                    loc=L
                ),
                else_clause=None,
                loc=L
            ),
            ast.Identifier(L, 'b'),
            ast.Identifier(L, 'c')
        ],
        loc=L
    )
    try:
        parse(tokenize('{ if true then { a } b c }'))
        assert False
    except Exception as e:
        assert 'expected ";"' in str(e)

    assert parse(tokenize('{ if true then { a } else { b } 3 }')) == ast.Block(
        expressions=[
            ast.IfExpression(
                cond=ast.Identifier(L, 'true'),
                then_clause=ast.Block(
                    expressions=[ast.Identifier(L, 'a')],
                    loc=L
                ),
                else_clause=ast.Block(
                    expressions=[ast.Identifier(L, 'b')],
                    loc=L
                ),
                loc=L
            ),
            ast.Literal(L, 3)
        ],
        loc=L
    )

    assert parse(tokenize('x = { { f(a) } { b } }')) == ast.BinaryOp(
        left=ast.Identifier(L, 'x'),
        op='=',
        right=ast.Block(
            expressions=[
                ast.Block(
                    expressions=[ast.FunctionCall(call=ast.Identifier(L, 'f'), args=[ast.Identifier(L, 'a')], loc=L)],
                    loc=L
                ),
                ast.Block(
                    expressions=[ast.Identifier(L, 'b')],
                    loc=L
                ),
            ],
            loc=L
        ),
        loc=L
    )

def test_parser_variable_dec() -> None:
    assert parse(tokenize('var x = 123')) == ast.VariableDec(
        variable=ast.Identifier(L, 'x'),
        value=ast.Literal(L, 123),
        loc=L
    )
    assert parse(tokenize('{var x = 123};')) == ast.Block(
        expressions=[
            ast.VariableDec(
                variable=ast.Identifier(L, 'x'),
                value=ast.Literal(L, 123),
                loc=L
            )
        ],
        loc=L
    )
    assert parse(tokenize('''
        {
            var x = 123;
            x = y
        };
        ''')) == ast.Block(
        expressions=[
            ast.VariableDec(
                variable=ast.Identifier(L, 'x'),
                value=ast.Literal(L, 123),
                loc=L
            ),
            ast.BinaryOp(
                left=ast.Identifier(L, 'x'),
                op='=',
                right=ast.Identifier(L, 'y'),
                loc=L
            ),       
        ],
        loc=L
    )
    assert parse(tokenize('''
        {
            x = y;
            var x = 123                          
        };
        ''')) == ast.Block(
        expressions=[
            ast.BinaryOp(
                left=ast.Identifier(L, 'x'),
                op='=',
                right=ast.Identifier(L, 'y'),
                loc=L
            ),            
            ast.VariableDec(
                variable=ast.Identifier(L, 'x'),
                value=ast.Literal(L, 123),
                loc=L
            ),
        ],
        loc=L
    )

def test_parser_location() -> None:
    assert parse(tokenize('{ if true then { a } else { b } 3 }')) == ast.Block(
        expressions=[
            ast.IfExpression(
                cond=ast.Identifier(Location(line=1, column=6), 'true'),
                then_clause=ast.Block(
                    expressions=[ast.Identifier(Location(line=1, column=18), 'a')],
                    loc=Location(line=1, column=16)
                ),
                else_clause=ast.Block(
                    expressions=[ast.Identifier(Location(line=1, column=29), 'b')],
                    loc=Location(line=1, column=27)
                ),
                loc=Location(line=1, column=3)
            ),
            ast.Literal(Location(line=1, column=33), 3)
        ],
        loc=Location(line=1, column=1)
    )
    assert parse(tokenize('''
        {
            x = y;
            var x = 123                          
        };
        ''')) == ast.Block(
        expressions=[
            ast.BinaryOp(
                left=ast.Identifier(Location(line=3, column=13), 'x'),
                op='=',
                right=ast.Identifier(Location(line=3, column=17), 'y'),
                loc=Location(line=3, column=13)
            ),            
            ast.VariableDec(
                variable=ast.Identifier(Location(line=4, column=17), 'x'),
                value=ast.Literal(Location(line=4, column=21), 123),
                loc=Location(line=4, column=13)
            ),
        ],
        loc=Location(line=2, column=9)
    )