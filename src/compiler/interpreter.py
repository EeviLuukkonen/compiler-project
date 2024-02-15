from typing import Any
from compiler import ast

Value = int | bool | None

def interpret(node: Any) -> Value:
    match node:
        case ast.Literal():
            return node.value
        
        case ast.BinaryOp():
            a: Any = interpret(node.left)
            b: Any = interpret(node.right)
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
                if interpret(node.cond):
                    return interpret(node.then_clause)
                else:
                    return interpret(node.else_clause)
            else:
                if interpret(node.cond):
                    interpret(node.then_clause)
                return None
        
        case _:
            raise Exception(f"Unsupported AST node {node}")