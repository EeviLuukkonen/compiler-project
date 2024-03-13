from compiler import ast
from compiler.symtab import SymTab
from compiler.types import Bool, Int, FunType, Type, Unit

def typecheck(node: ast.Module | ast.Expression, symtab: SymTab) -> Type:
    basic_types = ['Int', 'Bool', 'Unit']
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
                    if isinstance(node.var_type, ast.BasicTypeExpr):
                        if node.var_type.name not in basic_types:
                            raise TypeError(f'Unknown type: {node.var_type}')
                    elif isinstance(node.var_type, ast.FunTypeExpr):
                        for p in node.var_type.parameters:
                            if p.name not in basic_types:
                                raise TypeError(f'Unknown type: {p}')
                        if node.var_type.return_type.name not in basic_types:
                            raise TypeError(f'Unknown type: {node.var_type.return_type}')
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
                            raise TypeError(f"Function parameter at {arg.loc} has type {arg_t} but expects {param_t}")
                    return fun_type.return_type
                raise Exception(f'Unknown function: {node.call.name}')
            
            case ast.WhileLoop():
                t1 = typecheck(node.cond, symtab)
                if t1 is not Bool:
                    raise TypeError(f"While-loop condition was {t1}, expected boolean")
                t2 = typecheck(node.do, symtab)
                return t2

            case ast.Return():
                if node.value is None:
                    return Unit
                return typecheck(node.value, symtab)

            case _:
                raise Exception(f"Unsupported AST node {node}")

    def define_function_type(node: ast.FunDefinition, symtab: SymTab) -> Type:
        name = node.name.name
        param_t = [pt.convert_to_basic_type() for pt in node.param_types]
        declared_return_t = node.return_type.convert_to_basic_type()

        for pt in param_t:
            if pt.name not in basic_types:
                raise TypeError(f'Unknown parameter type {pt} in function definition')
        
        if declared_return_t.name not in ['Int', 'Bool', 'Unit']:
            raise TypeError(f'Unknown return type in function definition: {declared_return_t}')
        
        for param, param_type in zip(node.params, param_t):
            symtab.set_local(param.name, param_type)
        print(symtab)
        
        actual_return_t = typecheck(node.body, symtab)
        
        if actual_return_t != declared_return_t:
            raise TypeError(f'Function {name} expected return type {declared_return_t}, got {actual_return_t}')
        
        symtab.set_local(str(name), FunType(param_t, declared_return_t))
        return declared_return_t
    
    if isinstance(node, ast.Module): # first iteration with module
        for fun in node.funcs:
            fun_t = define_function_type(fun, symtab)
        if node.expr:
            expression_result_type = typecheck_expr(node.expr, symtab)
            node.expr.type = expression_result_type
        else: # source code only includes function definition(s), no expression
            return fun_t
    else: # other iterations with expression
        expression_result_type = typecheck_expr(node, symtab)
        node.type = expression_result_type

    return expression_result_type

