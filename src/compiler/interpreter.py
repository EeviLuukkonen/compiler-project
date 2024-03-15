from typing import Any
from compiler import ast

Value = int | bool | None

def interpret(node: ast.Module) -> Value:
    expr = node.expr
    def interpret_expr(node: ast.Expression | None) -> Value:
        match node:
            case ast.Literal():
                return node.value
            
            case ast.BinaryOp():
                a: Any = interpret_expr(node.left)
                b: Any = interpret_expr(node.right)
                if node.op == '+':
                    return a + b
                elif node.op == '-':
                    return a - b
                elif node.op == '*':
                    return a * b
                elif node.op == '/':
                    return a / b
                elif node.op == '//':
                    return a // b
                elif node.op == '>':
                    return a > b
                elif node.op == '<':
                    return a < b
                else:
                    raise Exception(f'Unsupported operator "{node.op}"')
                
            case ast.IfExpression():
                if node.else_clause is not None:
                    if interpret_expr(node.cond):
                        return interpret_expr(node.then_clause)
                    else:
                        return interpret_expr(node.else_clause)
                else:
                    if interpret_expr(node.cond):                        
                        return interpret_expr(node.then_clause)
                    return None
            
            case _:
                raise Exception(f"Unsupported AST node {node}")
    return interpret_expr(expr)