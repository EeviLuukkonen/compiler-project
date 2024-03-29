from compiler.tokenizer import tokenize, L, Location
from compiler.parser import parse
from compiler import ast

def parser_helper(s: str) -> ast.Expression | None:
    return parse(tokenize(s)).expr

def test_parser_expression() -> None:
    assert parser_helper("if 2 or 3 and a then jee + 1") == ast.IfExpression(
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
    assert parser_helper('if not not a then (1 + 2)') == ast.IfExpression(
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
    assert parser_helper('1+2 = 3') == ast.BinaryOp(
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
    assert parser_helper('2 = 1 = 3') == ast.BinaryOp(
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
    assert parser_helper('if 2 = 1+1 then -3') == ast.IfExpression(
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
    assert parser_helper('''
        1+2 = 3;
        true
    ''') == ast.Block(L, [
        ast.BinaryOp(
            left=ast.BinaryOp(
                left=ast.Literal(L, 1),
                op='+',
                right=ast.Literal(L, 2),
                loc=L
            ),
            op='=',
            right=ast.Literal(L, 3),
            loc=L
        ),
        ast.Literal(L, True)
    ])


def test_parser_block() -> None:
    assert parser_helper('''
        {
            f(a);
            x = y;
            f(x)
        };
        ''') == ast.Block(
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

    assert parser_helper('''
        {
            f(a);
            x = y;
            f(x);
        };
        ''') == ast.Block(
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
        parser_helper('''
            {
                f(a)
                x = y;
                f(x)
            };
        ''')
        assert False
    except Exception as e:
        assert 'expected ";"' in str(e)

    try:
        parser_helper('''
            {
                f(a);
                x = y;;
                f(x)
            };
        ''')
        assert False
    except Exception as e:
        assert 'Unknown syntax at' in str(e)

    assert parser_helper('if {a}; then {b};') == ast.IfExpression(
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
    assert parser_helper('{ ja }') == ast.Block(
        expressions=[
            ast.Identifier(L, 'ja')
        ],
        loc=L
    )
    assert parser_helper('{ 3 + { eka } { toka } }') == ast.Block(
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
    assert parser_helper('{ if true then { a } b; c }') == ast.Block(
        expressions=[
            ast.IfExpression(
                cond=ast.Literal(L, True),
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
        parser_helper('{ if true then { a } b c }')
        assert False
    except Exception as e:
        assert 'expected ";"' in str(e)

    assert parser_helper('{ if true then { a } else { b } 3 }') == ast.Block(
        expressions=[
            ast.IfExpression(
                cond=ast.Literal(L, True),
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

    assert parser_helper('x = { { f(a) } { b } }') == ast.BinaryOp(
        left=ast.Identifier(L, 'x'),
        op='=',
        right=ast.Block(
            expressions=[
                ast.Block(
                    expressions=[ast.FunctionCall(call=ast.Identifier(
                        L, 'f'), args=[ast.Identifier(L, 'a')], loc=L)],
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
    assert parser_helper('{var x = 1; {var x = true}; x}') == ast.Block(
        expressions=[
            ast.VariableDec(L, ast.Identifier(L, 'x'),
                            ast.Literal(L, 1), var_type=None),
            ast.Block(
                loc=L,
                expressions=[ast.VariableDec(L, ast.Identifier(
                    L, 'x'), ast.Literal(L, True), var_type=None)]
            ),
            ast.Identifier(L, 'x')
        ],
        loc=L
    )

    assert parser_helper('{1+{}; 1}') == ast.Block(
        loc=L,
        expressions=[
            ast.BinaryOp(
                loc=L,
                left=ast.Literal(L, 1),
                op='+',
                right=ast.Block(L, None)
            ),
            ast.Literal(L, 1)
        ]
    )


def test_multiple_expressions() -> None:
    assert parser_helper('1+2; x') == ast.Block(
        loc=L,
        expressions=[
            ast.BinaryOp(
                loc=L,
                left=ast.Literal(L, 1),
                op='+',
                right=ast.Literal(L, 2)
            ),
            ast.Identifier(L, 'x')
        ]
    )
    assert parser_helper('''var x = false;
    true or { x = true; true }; x''') == ast.Block(
        loc=L,
        expressions=[
            ast.VariableDec(
                variable=ast.Identifier(L, 'x'),
                value=ast.Literal(L, False),
                loc=L,
                var_type=None
            ),
            ast.BinaryOp(
                loc=L,
                left=ast.Literal(L, True),
                op='or',
                right=ast.Block(
                    loc=L,
                    expressions=[
                        ast.BinaryOp(loc=L, left=ast.Identifier(
                            L, 'x'), op='=', right=ast.Literal(L, True)),
                        ast.Literal(L, True)
                    ]
                )
            ),
            ast.Identifier(L, 'x')
        ]
    )


def test_bool_literal() -> None:
    assert parser_helper('true') == ast.Literal(
        loc=L,
        value=True
    )


def test_parser_variable_dec() -> None:
    assert parser_helper('var x = 123') == ast.VariableDec(
        variable=ast.Identifier(L, 'x'),
        value=ast.Literal(L, 123),
        loc=L,
        var_type=None
    )
    assert parser_helper('{var x = 123};') == ast.Block(
        expressions=[
            ast.VariableDec(
                variable=ast.Identifier(L, 'x'),
                value=ast.Literal(L, 123),
                loc=L,
                var_type=None
            )
        ],
        loc=L
    )
    assert parser_helper('''
        {
            var x = 123;
            x = y
        };
        ''') == ast.Block(
        expressions=[
            ast.VariableDec(
                variable=ast.Identifier(L, 'x'),
                value=ast.Literal(L, 123),
                loc=L,
                var_type=None
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
    assert parser_helper('''
        {
            x = y;
            var x = 123                          
        };
        ''') == ast.Block(
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
                loc=L,
                var_type=None
            ),
        ],
        loc=L
    )
    assert parser_helper('var x = {}') == ast.VariableDec(
        loc=L,
        variable=ast.Identifier(L, 'x'),
        value=ast.Block(loc=L, expressions=None),
        var_type=None
    )
    assert parser_helper('var x: Int = 2') == ast.VariableDec(
        loc=L,
        variable=ast.Identifier(L, 'x'),
        value=ast.Literal(L, 2),
        var_type=ast.Int
    )
    assert parser_helper('var x: I = 2') == ast.VariableDec(
        loc=L,
        variable=ast.Identifier(L, 'x'),
        value=ast.Literal(L, 2),
        var_type=ast.BasicTypeExpr('I')
    )
    assert parser_helper('var x: (Int, Bool) => Bool = 2') == ast.VariableDec(
        loc=L,
        variable=ast.Identifier(L, 'x'),
        value=ast.Literal(L, 2),
        var_type=ast.FunTypeExpr([ast.Int, ast.Bool], ast.Bool)
    )


def test_parser_location() -> None:
    assert parser_helper('{ if true then { a } else { b } 3 }') == ast.Block(
        expressions=[
            ast.IfExpression(
                cond=ast.Literal(Location(line=1, column=6), True),
                then_clause=ast.Block(
                    expressions=[ast.Identifier(
                        Location(line=1, column=18), 'a')],
                    loc=Location(line=1, column=16)
                ),
                else_clause=ast.Block(
                    expressions=[ast.Identifier(
                        Location(line=1, column=29), 'b')],
                    loc=Location(line=1, column=27)
                ),
                loc=Location(line=1, column=3)
            ),
            ast.Literal(Location(line=1, column=33), 3)
        ],
        loc=Location(line=1, column=1)
    )
    assert parser_helper('''
        {
            x = y;
            var x = 123                          
        };
        ''') == ast.Block(
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
                loc=Location(line=4, column=13),
                var_type=None
            ),
        ],
        loc=Location(line=2, column=9)
    )

def test_parser_loops() -> None:
    assert parser_helper("while true do 2") == ast.WhileLoop(
        cond=ast.Literal(L, True),
        do=ast.Literal(L, 2),
        loc=L
    )
    assert parser_helper("while true do break") == ast.WhileLoop(
        cond=ast.Literal(L, True),
        do=ast.BreakContinue(L, 'break'),
        loc=L
    )
    assert parser_helper("{if true then continue}") == ast.Block(
        expressions=[ast.IfExpression(
            cond=ast.Literal(L, True),
            then_clause=ast.BreakContinue(L, 'continue'),
            else_clause=None,
            loc=L
        )],
        loc=L
    )


def test_parser_functions() -> None:
    assert parse(tokenize(('fun f(a: Int): Int {return a}'))).funcs == [ast.FunDefinition(
        loc=L,
        name=ast.Identifier(L, 'f'),
        params=[ast.Identifier(L, 'a')],
        param_types=[ast.Int],
        return_type=ast.Int,
        body=ast.Block(
            loc=L,
            expressions=[
                ast.Return(L, ast.Identifier(L, 'a'))
            ]
        )
    )]

    assert parse(tokenize(('fun f(): Bool {return true}'))).funcs == [ast.FunDefinition(
        loc=L,
        name=ast.Identifier(L, 'f'),
        params=[],
        param_types=[],
        return_type=ast.Bool,
        body=ast.Block(
            loc=L,
            expressions=[
                ast.Return(L, ast.Literal(L, True))
            ]
        )
    )]

    try:
        parse(tokenize(('fun f(a: Int): Int {return a; return true}')))
        assert False
    except Exception as e:
            assert 'Return' in str(e)

