
from compiler import ast, ir
from compiler.ir import IRVar

def generate_ir(root_node: ast.Expression) -> list[ir.Instruction]:
    
    next_var_number = 1

    def new_var() -> IRVar:
        nonlocal next_var_number
        var = IRVar(f'x{next_var_number}')
        next_var_number += 1
        return var
    
    instructions = []

    def visit(node: ast.Expression) -> IRVar:
        match node:
            case ast.Literal():
                var = new_var()
                instructions.append(ir.LoadIntConst(node.value, var))
                return var

            case ast.BinaryOp():
                var_left = visit(node.left)
                var_right = visit(node.right)
                var_result = new_var()
                instructions.append(ir.Call(
                    fun=IRVar(node.op),
                    args=[var_left, var_right],
                    dest=var_result
                ))
                return var_result

            case _:
                raise Exception(f"Unstupported AST node: {node}")
    
    visit(root_node)
    return instructions