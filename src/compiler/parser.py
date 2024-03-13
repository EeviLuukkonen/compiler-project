from typing import List
from compiler import ast
from compiler.tokenizer import Location, Token

def parse(tokens: list[Token]) -> ast.Module:
    pos = 0

    def peek(offset: int = 0) -> Token:
        index = offset + pos
        if 0 <= index < len(tokens):
            return tokens[index]
        else:
            return Token(type='end', text='', loc=tokens[-1].loc)
        
    def consume(expected: str | list[str] | None = None) -> Token:
        token = peek()
        if isinstance(expected, str) and token.text != expected:
            raise Exception(f'{token.loc}: expected "{expected}", got "{token.text}"')
        if isinstance(expected, list) and token.text not in expected:
            comma_separated = ", ".join([f'"{e}"' for e in expected])
            raise Exception(f'{token.loc}: expected one of: {comma_separated}')
        nonlocal pos
        pos += 1
        return token

    def parse_module() -> ast.Module:
        expressions: List[ast.Expression] = []
        funcs: List[ast.FunDefinition] = []

        while pos < len(tokens):
            if peek().text == 'fun':
                fun = parse_fun_definition()
                funcs.append(fun)
            else:
                expression = parse_expression(parse_or())
                expressions.append(expression)

                if peek().text == ';':
                    consume(';')
                elif peek(-1).text in [';', '}']: # previous expression ends in a block
                    continue
                elif pos < len(tokens):
                    raise Exception(f'{peek().loc}: Expected ; between expressions, got {peek().text}')
            
        if len(expressions) == 1: # one top level expression
            return ast.Module(funcs=funcs, expr=expressions[0])
        elif len(expressions) == 0 and len(funcs) > 0: # only function definition(s)
            return ast.Module(funcs=funcs, expr=None)
        elif len(expressions) == 0 and len(funcs) == 0:
            raise Exception('Empty input!')

        return ast.Module(funcs=funcs, expr=ast.Block(Location(line=1, column=1), expressions))

    def parse_fun_definition() -> ast.FunDefinition:
        loc = peek().loc
        consume('fun')
        name = parse_identifier()
        consume('(')

        params: list[ast.Identifier] = []
        param_types: list[ast.BasicTypeExpr] = []

        while peek().text != ')':
            if len(params) > 0:
                consume(',')
            param = parse_identifier() # TODO: laajenna että funktiokutsu voi olla parametrina
            consume(':')
            param_type = ast.BasicTypeExpr(consume().text)

            params.append(param)
            param_types.append(param_type)

        consume(')')
        consume(':')

        return_type = ast.BasicTypeExpr(consume().text)

        body = parse_block()

        return ast.FunDefinition(
            loc,
            name,
            params,
            param_types,
            body,
            return_type
        )

    def parse_expression(left: ast.Expression) -> ast.Expression:
        if peek().text == '=':
            operator = consume().text
            right = parse_expression(parse_or())
            return ast.BinaryOp(
                left.loc,
                left,
                operator,
                right
            )
        else:
            return left

    def parse_or() -> ast.Expression:
        left = parse_and()
        loc = left.loc

        while peek().text == 'or':
            operator = consume().text
            right = parse_and()
            left = ast.BinaryOp(
                loc,
                left,
                operator,
                right
            )
        return left

    def parse_and() -> ast.Expression:
        left = parse_eq_comparison()
        loc = left.loc

        while peek().text == 'and':
            operator = consume().text
            right = parse_eq_comparison()
            left = ast.BinaryOp(
                loc,
                left,
                operator,
                right
            )
        return left
    
    def parse_eq_comparison() -> ast.Expression:
        left = parse_comparison()
        loc = left.loc

        while peek().text in ['!=', '==']:
            operator_token = consume()
            operator = operator_token.text
            loc = operator_token.loc

            right = parse_comparison()
            left = ast.BinaryOp(
                loc,
                left,
                operator,
                right
            )
        return left

    def parse_comparison() -> ast.Expression:
        left = parse_polynomial()
        loc = left.loc

        while peek().text in ['<', '>', '<=', '>=', '>=']:
            operator_token = consume()
            operator = operator_token.text
            loc = operator_token.loc

            right = parse_polynomial()

            left = ast.BinaryOp(
                loc,
                left,
                operator,
                right
            )
        return left
    
    def parse_polynomial() -> ast.Expression:
        left = parse_term()
        loc = left.loc

        while peek().text in ['+', '-']:
            operator_token = consume()
            operator = operator_token.text
            loc = operator_token.loc

            right = parse_term()
            left = ast.BinaryOp(
                loc,
                left,
                operator,
                right
            )
        return left

    def parse_term() -> ast.Expression:
        left = parse_unary()
        loc = left.loc

        while peek().text in ['*', '/', '%']:
            operator_token = consume()
            operator = operator_token.text
            right = parse_unary()
            left = ast.BinaryOp(
                loc,
                left,
                operator,
                right
            )
        return left
    
    def parse_unary() -> ast.Expression:
        if peek().text in ['not', '-']:
            operator_token = consume()
            operator = operator_token.text
            loc = operator_token.loc

            right = parse_unary()
            left = ast.UnaryOp(
                loc,
                operator,
                right
            )
            return left
        else:
            return parse_factor()

    def parse_factor() -> ast.Expression:
        if peek().text == 'var':
            return parse_variable_dec()
        elif peek().text == '(':
            return parse_parenthesized()
        elif peek().text == 'if':
            return parse_if()
        elif peek().text in ['true', 'false']:
            return parse_bool_literal()
        elif peek().text == 'while':
            return parse_while_loop()
        elif peek().type == 'int_literal':
            return parse_int_literal()
        elif peek().type == 'identifier':
            identifier = parse_identifier()
            if peek().text == '(': # function call
                return parse_arguments(identifier)
            return identifier
        elif peek().text == '{':
            return parse_block()
        else:
            raise Exception(f'Unknown syntax at {peek().loc}')

    def parse_variable_dec() -> ast.VariableDec:
        loc = peek().loc
        if peek().loc.column == 1 or peek(-1).text in ['{', ';']:
            consume('var')
            identifier = parse_identifier()
            var_type = None

            if peek().text == ":":
                consume(':')
                var_type = parse_type_expression()

            consume('=')
            value = parse_expression(parse_or())
            return ast.VariableDec(loc, identifier, value, var_type)
        else:
            raise Exception("Variable declaration should only appear as a top level expression!")

    def parse_type_expression() -> ast.TypeExpr:
        if peek().text == '(':
            return parse_func_type_expression()
        else:
            token = consume()
            return ast.BasicTypeExpr(token.text)
        
    def parse_func_type_expression() -> ast.FunTypeExpr:
        consume('(')
        parameters: list[ast.BasicTypeExpr] = []
        while True:
            parameters.append(parse_type_expression()) # type: ignore[arg-type]
            if peek().text == ',':
                consume(',')
            else:
                break
        consume(')')
        consume('=>')
        return_type = parse_type_expression()

        return ast.FunTypeExpr(parameters, return_type) # type: ignore[arg-type]

    def parse_if() -> ast.Expression:
        loc = peek().loc
        consume('if')
        cond = parse_expression(parse_or())
        consume('then')
        then_clause = parse_expression(parse_or())
        if peek().text == "else":
            consume('else')
            else_clause = parse_expression(parse_or())
        else:
            else_clause = None
        return ast.IfExpression(loc, cond, then_clause, else_clause)

    def parse_while_loop() -> ast.Expression:
        loc = peek().loc
        consume('while')
        cond = parse_expression(parse_or())
        consume('do')
        do = parse_expression(parse_or())
        return ast.WhileLoop(loc, cond, do)
    
    def parse_parenthesized() -> ast.Expression:
        consume('(')
        expr = parse_comparison()
        consume(')')
        return expr
    
    def parse_bool_literal() -> ast.Literal:
        token = peek()
        if token.text == 'true':
            consume()
            return ast.Literal(value=bool(True), loc=token.loc)
        elif token.text == 'false':
            consume()
            return ast.Literal(value=bool(False), loc=token.loc)
        else:
            raise Exception(f'Expected integer literal, found "{token.text}"')

    def parse_int_literal() -> ast.Literal:
        token = peek()
        if token.type == 'int_literal':
            consume()
            return ast.Literal(value=int(token.text), loc=token.loc)
        else:
            raise Exception(f'Expected integer literal, found "{token.text}"')
        
    def parse_return() -> ast.Return:
        loc = peek().loc
        consume('return')
        if peek().text == '}':
            value = None
        else:
            value = parse_expression(parse_or())
        if peek().text != '}':
            raise Exception(f'Return statement must be the last statement in a block')
        return ast.Return(loc, value)

    def parse_identifier() -> ast.Identifier:
        token = peek()
        if token.type == 'identifier':
            consume()
            return ast.Identifier(loc=token.loc, name=token.text)
        else:
            raise Exception(f'Expected identifier, found "{token.text}"')
    
    def parse_arguments(call: ast.Identifier) -> ast.FunctionCall:
        loc = peek().loc
        consume('(')
        args: List[ast.Expression] = []

        while peek().text != ')':
            if args:
                consume(',')
            arg = parse_expression(parse_or())
            args.append(arg)
        consume(')')
        return ast.FunctionCall(loc, call, args)
    
    def parse_block() -> ast.Block:
        loc = peek().loc
        consume('{')
        expressions: List[ast.Expression] = []

        while peek().text != '}':
            if peek().text == 'return':
                expressions.append(parse_return())
                semicolon = False
            else:
                expression = parse_expression(parse_or())
                expressions.append(expression)

                semicolon = False
                if peek().text == '}': # block ends
                    break
                if isinstance(expressions[-1], ast.Block): # previous expression is a block
                    if peek().text == ';':
                        consume(';')
                        semicolon = True
                elif peek(-1).text == '}': # expression inside a block ends in a block
                    if peek().text == ';':
                        consume(';')
                        semicolon = True
                else:
                    consume(';')
                    semicolon = True
        consume('}')
        
        if not expressions: # empty block
            return ast.Block(loc, None)

        if semicolon:  # last semicolon inside block is present and result expression is none
            expressions.append(ast.Literal(loc, None))

        if peek().text == ";": # optional last semicolon after block
            consume(';')
            semicolon = True

        return ast.Block(loc, expressions)

    return parse_module()
