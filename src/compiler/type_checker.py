from compiler import ast
from compiler.types import Bool, Int, SymTab, FunType, Type, Unit


def typecheck(node: ast.Expression | None, symtab: SymTab) -> Type:
    match node:
        case ast.Literal():
            if isinstance(node.value, bool):
                return Bool
            elif isinstance(node.value, int):
                return Int
            else:
                raise Exception(f"Don't know the type of literal: {node.value}")
            
        case ast.BinaryOp():
            t1 = typecheck(node.left, symtab)
            t2 = typecheck(node.right, symtab)
            if node.op in ['=', '==', '!=']:
                if t1 != t2:
                    raise TypeError(f'Operator {node.op} expected same type on each side, got {t1} and {t2}')
                return t1
            op_type = symtab.get_type(node.op)
            if isinstance(op_type, FunType):
                if op_type.parameters != [t1, t2]:
                    raise TypeError(f'Operator {node.op} expected {op_type.parameters}, got {t1} and {t2}')
                return op_type.return_type
            raise Exception(f'Unknown operator: {node.op}')
        
        case ast.Identifier():
            t = symtab.get_type(node.name)
            if t not in [Int, Bool]:
                raise Exception(f"Unknown variable type {t}")
            return t
            
        case ast.IfExpression():
            t1 = typecheck(node.cond, symtab)
            if t1 is not Bool:
                raise TypeError(f'If condition was {t1}, expected boolean')
            t2 = typecheck(node.then_clause, symtab)
            if node.else_clause is None:
                return Unit
            t3 = typecheck(node.else_clause, symtab)
            if t2 != t3:
                raise TypeError(f'then and else had different types: {t2} and {t3}')
            return t2
        
        case ast.VariableDec():
            name = node.variable.name
            t = typecheck(node.value, symtab)
            symtab.set_type(str(name), t)
            return Unit

        case ast.Block():
            if node.expressions is not None:
                symtab_block = symtab.create_inner_tab()
                for expression in node.expressions:
                    t = typecheck(expression, symtab_block)
            else:
                raise Exception(f'Empty block')
            return t
        
        case ast.UnaryOp():
            op_type = symtab.get_type(f'unary_{node.op}')
            t = typecheck(node.right, symtab)
            if op_type != t:
                raise TypeError(f'Operator "unary_{node.op}" right side expected {op_type}, got {t}')
            return t
        
        case ast.FunctionCall():
            fun_type = symtab.get_type(node.call.name)
            args = node.args
            if isinstance(fun_type, FunType):
                if len(args) != len(fun_type.parameters):        
                    raise TypeError(f"Function expects {len(fun_type.parameters)} parameter(s) but {len(args)} were given")
                for arg, param_t in zip(args, fun_type.parameters):
                    arg_t = typecheck(arg, symtab)
                    if arg_t != param_t:
                        raise TypeError(f"Function parameter {arg} has type {arg_t} but expects {param_t}")
                return fun_type.return_type
            raise Exception(f'Unknown function: {node.call.name}')
        
        case ast.WhileLoop():
            t1 = typecheck(node.cond, symtab)
            if t1 is not Bool:
                raise TypeError(f"While-loop condition was {t1}, expected boolean")
            t2 = typecheck(node.do, symtab)
            return t2

        case _:
            raise Exception(f"Unsupported AST node {node}")