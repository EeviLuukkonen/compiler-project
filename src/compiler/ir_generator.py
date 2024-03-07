from compiler import ast, ir
from compiler.ir import IRVar
from compiler.symtab import SymTab
from compiler.tokenizer import Location
from compiler.types import Bool, Int, Type, Unit

def generate_ir(root_types: dict[IRVar, Type], root_node: ast.Module) -> dict[str, list[ir.Instruction]]:
    var_types: dict[IRVar, Type] = root_types.copy()

    var_unit = IRVar('unit')
    var_types[var_unit] = Unit

    next_var_number = 1
    next_label_number = 1

    def new_var(t: Type) -> IRVar:
        nonlocal next_var_number
        var = IRVar(f'x{next_var_number}')
        var_types[var] = t
        next_var_number += 1
        return var
    
    def new_label() -> ir.Label:
        nonlocal next_label_number
        label = ir.Label(Location(line=1, column=1), f'L{next_label_number}')
        next_label_number += 1
        return label
    
    instructions: dict[str, list[ir.Instruction]] = {'main': []}

    def visit_module(st: SymTab[IRVar], root_node: ast.Module) -> IRVar:
        return visit_expr(st, root_node.expr)

    def visit_expr(st: SymTab[IRVar], node: ast.Expression, func_name: str = 'main') -> IRVar:
        loc = node.loc
        match node:
            case ast.Literal():
                match node.value:
                    case bool():
                        var = new_var(Bool)
                        instructions[func_name].append(ir.LoadBoolConst(
                            loc, node.value, var
                        ))
                    case int():
                        var = new_var(Int)
                        instructions[func_name].append(ir.LoadIntConst(
                            loc, node.value, var
                        ))
                    case None:
                        var = var_unit
                    case _:
                        raise Exception(f"{loc}: unsupported literal: {type(node.value)}")
                return var
            
            case ast.Identifier():
                return st.get_symbol(node.name)

            case ast.BinaryOp(op='='):
                if not isinstance(node.left, ast.Identifier):
                    raise Exception(f"{loc}: Left side of assignment must be a variable name")

                var_right = visit_expr(st, node.right)
                var_left = visit_expr(st, node.left)
                instructions[func_name].append(ir.Copy(
                    loc, var_right, var_left
                ))
                return var_unit
            
            case ast.BinaryOp(op='or'):
                l_skip = new_label()
                l_right = new_label()
                l_end = new_label()

                var_left = visit_expr(st, node.left)
                instructions[func_name].append(ir.CondJump(loc, var_left, l_skip, l_right))

                instructions[func_name].append(l_right)
                var_right = visit_expr(st, node.right)
                var_result = new_var(Bool)
                instructions[func_name].append(ir.Copy(loc, var_right, var_result))
                instructions[func_name].append(ir.Jump(loc, l_end))

                instructions[func_name].append(l_skip)
                instructions[func_name].append(ir.LoadBoolConst(loc, True, var_result))

                instructions[func_name].append(l_end)
                return var_result

            case ast.BinaryOp(op='and'):
                l_right = new_label()
                l_skip = new_label()
                l_end = new_label()

                var_left = visit_expr(st, node.left)
                instructions[func_name].append(ir.CondJump(loc, var_left, l_right, l_skip))

                instructions[func_name].append(l_right)
                var_right = visit_expr(st, node.right)
                var_result = new_var(Bool)
                instructions[func_name].append(ir.Copy(loc, var_right, var_result))
                instructions[func_name].append(ir.Jump(loc, l_end))

                instructions[func_name].append(l_skip)
                instructions[func_name].append(ir.LoadBoolConst(loc, False, var_result))

                instructions[func_name].append(l_end)
                return var_result

            case ast.BinaryOp():
                var_op = st.get_symbol(node.op)
                var_left = visit_expr(st, node.left)
                var_right = visit_expr(st, node.right)
                var_result = new_var(node.type)
                instructions[func_name].append(ir.Call(
                    location=loc,
                    fun=var_op,
                    args=[var_left, var_right],
                    dest=var_result
                ))
                return var_result
            
            case ast.IfExpression():
                if node.else_clause is None:
                    l_then = new_label()
                    l_end = new_label()

                    var_cond = visit_expr(st, node.cond)

                    instructions[func_name].append(ir.CondJump(loc, var_cond, l_then, l_end))
                    
                    instructions[func_name].append(l_then)
                    visit_expr(st, node.then_clause)
                    instructions[func_name].append(l_end)
                    return var_unit
                else:
                    l_then = new_label()
                    l_else = new_label()
                    l_end = new_label()

                    var_cond = visit_expr(st, node.cond)
                    instructions[func_name].append(ir.CondJump(loc, var_cond, l_then, l_else))

                    instructions[func_name].append(l_then)
                    var_result = visit_expr(st, node.then_clause)
                    instructions[func_name].append(ir.Jump(loc, l_end))

                    instructions[func_name].append(l_else)
                    var_else_result = visit_expr(st, node.else_clause)
                    instructions[func_name].append(ir.Copy(loc, var_else_result, var_result))

                    instructions[func_name].append(l_end)
                    return var_result
                
            case ast.VariableDec():
                var_value = visit_expr(st, node.value)
                var_result = new_var(var_types[var_value])

                st.set_local(node.variable.name, var_result)

                instructions[func_name].append(ir.Copy(loc, var_value, var_result))
                return var_result
            
            case ast.Block():
                block_st = st.create_inner_tab()
                if node.expressions is not None:
                    for e in node.expressions:
                        var_result = visit_expr(block_st, e)
                    return var_result
                return new_var(Unit)
            
            case ast.FunctionCall():
                var_call = st.get_symbol(node.call.name)
                var_args = []
                for expr in node.args:
                    var_arg = visit_expr(st, expr)
                    var_args.append(var_arg)
                var_result = new_var(node.type)
                instructions[func_name].append(ir.Call(loc, var_call, var_args, var_result))
                return var_result
            
            case ast.WhileLoop():
                l_cond = new_label()
                l_body = new_label()
                l_end = new_label()

                instructions[func_name].append(l_cond)
                var_cond = visit_expr(st, node.cond)
                instructions[func_name].append(ir.CondJump(loc, var_cond, l_body, l_end))

                instructions[func_name].append(l_body)
                visit_expr(st, node.do)
                instructions[func_name].append(ir.Jump(loc, l_cond))

                instructions[func_name].append(l_end)
                return var_unit
            
            case ast.UnaryOp():
                var_right = visit_expr(st, node.right)
                var_result = new_var(var_types[var_right])
                var_op = st.get_symbol(f'unary_{node.op}')
                instructions[func_name].append(ir.Call(
                    loc, var_op, [var_right], var_result
                ))
                return var_result

            case _:
                raise Exception(f"Unsupported AST node: {node}")
    
    root_symtab = SymTab[IRVar](locals={}, parent=None)
    for v in root_types.keys():
        root_symtab.set_local(v.name, v)

    var_result = visit_module(root_symtab, root_node)

    if var_types[var_result] == Int:
        instructions['main'].append(ir.Call(
            Location(line=0, column=0), # pseudo location used for print calls
            IRVar("print_int"),
            [var_result],
            new_var(Unit)
        ))
    elif var_types[var_result] == Bool:
        instructions['main'].append(ir.Call(
            Location(line=0, column=0),
            IRVar("print_bool"),
            [var_result],
            new_var(Unit)
        ))

    return instructions
