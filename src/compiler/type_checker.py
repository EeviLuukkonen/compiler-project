from compiler import ast
from compiler.symtab import SymTab
from compiler.types import Bool, Int, FunType, Type, Unit

def typecheck(node: ast.Module | ast.Expression, symtab: SymTab) -> Type:
    def define_function_type(node: ast.FunDefinition, symtab: SymTab) -> None:
        name = node.name.name
        param_t = [Int] # TODO: fix
        return_t = node.return_type
        symtab.set_local(str(name), FunType(param_t, return_t))

    def typecheck_expr(node: ast.Expression, symtab: SymTab) -> Type:
        match node:
            case ast.Literal():
                if isinstance(node.value, bool):
                    return Bool
                elif isinstance(node.value, int):
                    return Int
                elif node.value is None:
                    return Unit
                else:
                    raise Exception(f"Don't know the type of literal: {node.value} at {node.loc}")
                
            case ast.BinaryOp():
                t1 = typecheck(node.left, symtab)
                t2 = typecheck(node.right, symtab)
                if node.op == '=':
                    if t1 != t2:
                        raise TypeError(f'Operator {node.op} expected same type on each side, got {t1} and {t2}')
                    return t1
                elif node.op in ['==', '!=']:
                    if t1 != t2:
                        raise TypeError(f'Operator {node.op} expected same type on each side, got {t1} and {t2}')
                    return Bool
                op_type = symtab.get_symbol(node.op)
                if isinstance(op_type, FunType):
                    if op_type.parameters != [t1, t2]:
                        raise TypeError(f'Operator {node.op} expected {op_type.parameters}, got {t1} and {t2}')
                    return op_type.return_type
                raise Exception(f'Unknown operator: {node.op}')
            
            case ast.Identifier():
                t = symtab.get_symbol(node.name)
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
                    raise TypeError(f'Then and else had different types: {t2} and {t3}')
                return t2
            
            case ast.VariableDec():
                name = node.variable.name
                t = typecheck(node.value, symtab)
                if node.var_type:
                    if not node.var_type == t:
                        raise TypeError(f'Variable {name} expected type {node.var_type}, got {t}')
                symtab.set_local(str(name), t)
                return Unit

            case ast.Block():
                if node.expressions is not None:
                    symtab_block = symtab.create_inner_tab()
                    for expression in node.expressions:
                        t = typecheck(expression, symtab_block)
                    return t
                return Unit
            
            case ast.UnaryOp():
                op_type = symtab.get_symbol(f'unary_{node.op}')
                t = typecheck(node.right, symtab)
                if op_type != t:
                    raise TypeError(f'Operator "unary_{node.op}" right side expected {op_type}, got {t}')
                return t
            
            case ast.FunctionCall():
                fun_type = symtab.get_symbol(node.call.name)
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
    
    if isinstance(node, ast.Module):
        for fun in node.funcs:
            define_function_type(fun, symtab)
        print(symtab)
        expression_result_type = typecheck_expr(node.expr, symtab)
        node.expr.type = expression_result_type
    else:
        expression_result_type = typecheck_expr(node, symtab)
        node.type = expression_result_type

    return expression_result_type

