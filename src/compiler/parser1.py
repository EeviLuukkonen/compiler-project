from typing import List
from compiler import ast
from compiler.tokenizer import Token


def parse(tokens: list[Token]) -> ast.Expression:
    pos = 0

    def peek() -> Token:
        if len(tokens) == 0:
            return Token(type='end', text='')
        if pos < len(tokens):
            return tokens[pos]
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
                left,
                operator,
                right
            )
        else:
            return left

    def parse_or() -> ast.Expression:
        left = parse_and()

        while peek().text == 'or':
            operator = consume().text
            right = parse_and()
            left = ast.BinaryOp(
                left,
                operator,
                right
            )
        return left

    def parse_and() -> ast.Expression:
        left = parse_eq_comparison()

        while peek().text == 'and':
            operator = consume().text
            right = parse_eq_comparison()
            left = ast.BinaryOp(
                left,
                operator,
                right
            )
        return left
    
    def parse_eq_comparison() -> ast.Expression:
        left = parse_comparison()

        while peek().text in ['!=', '==']:
            operator = consume().text
            right = parse_comparison()
            left = ast.BinaryOp(
                left,
                operator,
                right
            )
        return left

    def parse_comparison() -> ast.Expression:
        left = parse_polynomial()

        while peek().text in ['<', '>', '<=', '>=', '>=']:
            operator_token = consume()
            operator = operator_token.text

            right = parse_polynomial()

            left = ast.BinaryOp(
                left,
                operator,
                right
            )
        return left
    
    def parse_polynomial() -> ast.Expression:
        left = parse_term()
        while peek().text in ['+', '-']:
            operator = consume().text
            right = parse_term()
            left = ast.BinaryOp(
                left,
                operator,
                right
            )
        return left

    def parse_term() -> ast.Expression:
        left = parse_unary()
        while peek().text in ['*', '/', '%']:
            operator_token = consume()
            operator = operator_token.text
            right = parse_unary()
            left = ast.BinaryOp(
                left,
                operator,
                right
            )
        return left
    
    def parse_unary() -> ast.Expression:
        if peek().text in ['not', '-']:
            operator = consume().text
            right = parse_unary()
            left = ast.UnaryOp(
                operator,
                right
            )
            return left
        else:
            return parse_factor()

    def parse_factor() -> ast.Expression:
        if peek().text == '(':
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
        elif peek().loc == None:
            raise Exception(f'Empty input!')
        else:
            raise Exception(f'{peek().loc}: expected an integer literal or an identifier')
        
    def parse_if() -> ast.Expression:
        consume('if')
        cond = parse_expression(parse_or())
        consume('then')
        then_clause = parse_expression(parse_or())
        if peek().text == "else":
            consume('else')
            else_clause = parse_expression(parse_or())
        else:
            else_clause = None
        return ast.IfExpression(cond, then_clause, else_clause)
    
    def parse_parenthesized() -> ast.Expression:
        consume('(')
        expr = parse_polynomial()
        consume(')')
        return expr
    
    def parse_int_literal() -> ast.Literal:
        token = peek()
        if token.type == 'int_literal':
            consume()
            return ast.Literal(value=int(token.text))
        else:
            raise Exception(f'Expected integer literal, found "{token.text}"')
        
    def parse_identifier() -> ast.Identifier:
        token = peek()
        if token.type == 'identifier':
            consume()
            return ast.Identifier(name=token.text)
        else:
            raise Exception(f'Expected integer literal, found "{token.text}"')
    
    def parse_arguments(call: ast.Identifier) -> ast.FunctionCall:
        consume('(')
        args: List[ast.Expression] = []

        while peek().text != ')':
            if args:
                consume(',')
            arg = parse_expression(parse_or())
            args.append(arg)
        consume(')')
        return ast.FunctionCall(call, args)
    
    def parse_block() -> ast.Block:
        consume('{')
        statements: List[ast.Expression] = []

        while peek().text != '}':
            statement = parse_expression(parse_or())
            statements.append(statement)

            semicolon = False
            if statements and peek().text != '}':
                consume(';')
                semicolon = True
        
        if semicolon: # last semicolon is present and result expression is none
            statements.append(ast.Literal(None))

        consume('}')

        return ast.Block(statements=statements)

    result = parse_expression(parse_or())

    if pos == len(tokens):
        return result
    else:
        raise Exception(f'Unknown syntax at the end of the code: {tokens[pos].loc}')
