from compiler import ast
from compiler.symtab import SymTab
from compiler.types import Bool, Int, FunType, Type, Unit

def typecheck(node: ast.Module, symtab: SymTab[Type]) -> Type:
    basic_types = ['Int', 'Bool', 'Unit']
    def typecheck_expr(node: ast.Expression, symtab: SymTab[Type]) -> Type:
        match node:
            case ast.Literal():
                if isinstance(node.value, bool):
                    return assign_type_to_expr(node, Bool)
                elif isinstance(node.value, int):
                    return assign_type_to_expr(node, Int)
                elif node.value is None:
                    return assign_type_to_expr(node, Unit)
                else:
                    raise Exception(f"Don't know the type of literal: {node.value} at {node.loc}")
                
            case ast.BinaryOp():
                t1 = typecheck_expr(node.left, symtab)
                t2 = typecheck_expr(node.right, symtab)
                if node.op == '=':
                    if t1 != t2:
                        raise TypeError(f'Operator {node.op} expected same type on each side, got {t1} and {t2}')
                    return assign_type_to_expr(node, t1)
                elif node.op in ['==', '!=']:
                    if t1 != t2:
                        raise TypeError(f'Operator {node.op} expected same type on each side, got {t1} and {t2}')
                    return assign_type_to_expr(node, Bool)
                op_type = symtab.get_symbol(node.op)
                if isinstance(op_type, FunType):
                    if op_type.parameters != [t1, t2]:
                        raise TypeError(f'Operator {node.op} expected {op_type.parameters}, got {t1} and {t2}')
                    return assign_type_to_expr(node, op_type.return_type)
                raise Exception(f'Unknown operator: {node.op}')
            
            case ast.Identifier():
                t = symtab.get_symbol(node.name)
                return assign_type_to_expr(node, t)
                
            case ast.IfExpression():
                t1 = typecheck_expr(node.cond, symtab)
                if t1 is not Bool:
                    raise TypeError(f'If condition was {t1}, expected boolean')
                t2 = typecheck_expr(node.then_clause, symtab)
                if node.else_clause is None:
                    return assign_type_to_expr(node, Unit)
                t3 = typecheck_expr(node.else_clause, symtab)
                if t2 != t3:
                    raise TypeError(f'Then and else had different types: {t2} and {t3}')
                return assign_type_to_expr(node, t2)
            
            case ast.VariableDec():
                name = node.variable.name
                if name in symtab.locals:
                    raise TypeError(f'Variable {name} is already declared in this scope')
                t = typecheck_expr(node.value, symtab)
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
                return assign_type_to_expr(node, Unit)

            case ast.Block():
                if node.expressions is not None:
                    symtab_block = symtab.create_inner_tab()
                    for expression in node.expressions:
                        t = typecheck_expr(expression, symtab_block)
                    return assign_type_to_expr(node, t)
                return assign_type_to_expr(node, Unit)
            
            case ast.UnaryOp():
                op_type = symtab.get_symbol(f'unary_{node.op}')
                t = typecheck_expr(node.right, symtab)
                if op_type != t:
                    raise TypeError(f'Operator "unary_{node.op}" right side expected {op_type}, got {t}')
                return assign_type_to_expr(node, t)
            
            case ast.FunctionCall():
                fun_name = node.call.name
                args = node.args
                try:
                    fun_type = symtab.get_symbol(fun_name)
                except TypeError:
                    raise TypeError(f'Function {fun_name} is called but never defined')
                if isinstance(fun_type, FunType):
                    if len(args) != len(fun_type.parameters):        
                        raise TypeError(f"Function expects {len(fun_type.parameters)} parameter(s) but {len(args)} were given")
                    for arg, param_t in zip(args, fun_type.parameters):
                        arg_t = typecheck_expr(arg, symtab)
                        if arg_t != param_t:
                            raise TypeError(f"Function parameter at {arg.loc} has type {arg_t} but expects {param_t}")
                    return assign_type_to_expr(node, fun_type.return_type)
                raise Exception(f'Unknown function: {fun_name}')

            case ast.WhileLoop():
                t1 = typecheck_expr(node.cond, symtab)
                if t1 is not Bool:
                    raise TypeError(f"While-loop condition was {t1}, expected boolean")
                t2 = typecheck_expr(node.do, symtab)
                return assign_type_to_expr(node, Unit)

            case ast.Return():
                if node.value is None:
                    return assign_type_to_expr(node, Unit)
                return typecheck_expr(node.value, symtab)
            
            case ast.BreakContinue():
                return assign_type_to_expr(node, Unit)

            case _:
                raise Exception(f"Unsupported AST node {node}")
    
    def assign_type_to_expr(node: ast.Expression, t: Type) -> Type:
        node.type = t
        return t

    def typecheck_function_def(node: ast.FunDefinition, symtab: SymTab) -> Type:
        name = node.name.name
        param_t = [pt.convert_to_basic_type() for pt in node.param_types]
        declared_return_t = node.return_type.convert_to_basic_type()

        symtab.set_local(str(name), FunType(param_t, declared_return_t))

        for pt in param_t:
            if pt.name not in basic_types:
                raise TypeError(f'Unknown parameter type {pt} in function definition')
        
        if declared_return_t.name not in ['Int', 'Bool', 'Unit']:
            raise TypeError(f'Unknown return type in function definition: {declared_return_t}')
        
        for param, param_type in zip(node.params, param_t):
            symtab.set_local(param.name, param_type)

        return declared_return_t
    
    def check_function_return_type(node: ast.FunDefinition, symtab: SymTab) -> None:
        actual_return_t = typecheck_expr(node.body, symtab)
        declared_return_t = node.return_type.convert_to_basic_type()
        if actual_return_t != declared_return_t:
            raise TypeError(f'Function {node.name.name} expected return type {declared_return_t}, got {actual_return_t}')


    def typecheck_module(node: ast.Module, symtab: SymTab[Type]) -> Type:
        for fun in node.funcs:
            fun_t = typecheck_function_def(fun, symtab)

        for fun in node.funcs:  
            check_function_return_type(fun, symtab)

        if node.expr:
            expression_result_type = typecheck_expr(node.expr, symtab)
            node.expr.type = expression_result_type
            return expression_result_type
        else: # source code only includes function definition(s), no expression
            return fun_t

    return typecheck_module(node, symtab)
