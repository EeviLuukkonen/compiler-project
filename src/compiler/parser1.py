from typing import List
from compiler import ast
from compiler.tokenizer import Token


def parse(tokens: list[Token]) -> ast.Expression:
    pos = 0

    def peek(offset: int = 0) -> Token:
        if len(tokens) == 0:
            raise Exception('Empty input!')
        index = offset + pos
        if 0 <= index < len(tokens):
            return tokens[index]
        else:
            return Token(type='end', text='', loc=tokens[-1].loc)
        
    def consume(expected: str | list[str] | None = None) -> Token:
        token = peek()
        if isinstance(expected, str) and token.text != expected:
            raise Exception(f'{token.loc}: expected "{expected}"')
        if isinstance(expected, list) and token.text not in expected:
            comma_separated = ", ".join([f'"{e}"' for e in expected])
            raise Exception(f'{token.loc}: expected one of: {comma_separated}')
        nonlocal pos
        pos += 1
        return token

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
            consume('=')
            value = parse_expression(parse_or())
            return ast.VariableDec(loc, identifier, value)
        else:
            raise Exception("Variable declaration should only appear as a top level expression!")

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
    
    def parse_parenthesized() -> ast.Expression:
        consume('(')
        expr = parse_polynomial()
        consume(')')
        return expr
    
    def parse_int_literal() -> ast.Literal:
        token = peek()
        if token.type == 'int_literal':
            consume()
            return ast.Literal(value=int(token.text), loc=token.loc)
        else:
            raise Exception(f'Expected integer literal, found "{token.text}"')
        
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
            expression = parse_expression(parse_or())
            expressions.append(expression)

            semicolon = False
            if peek().text == '}': # block ends
                break
            elif peek(-1).text == '}': # expression inside a block ends in a block
                if peek().text == ';': # only consumes optional semicolon if it exists
                    consume(';')
                pass
            else:
                consume(';')
                semicolon = True

        if semicolon:  # last semicolon is present and result expression is none
            expressions.append(ast.Literal(loc, None))

        consume('}')

        if peek().text == ";": # optional last semicolon
            consume(';')

        return ast.Block(loc, expressions)

    result = parse_expression(parse_or())

    if pos == len(tokens):
        return result
    else:
        raise Exception(f'Unknown syntax at the end of the code: {tokens[pos].loc}')
