import dataclasses
from compiler import ir
from compiler.intrinsics import IntrinsicArgs, all_intrinsics

def generate_assembly(instructions: dict[str, list[ir.Instruction]]) -> str:
    assembly_code_lines = []
    def emit(line: str) -> None: assembly_code_lines.append(line)

    locals = Locals(get_all_ir_variables(instructions))

    emit('.global main')
    emit('.type main, @function')
    emit('.extern print_int')
    emit('.extern print_bool')
    emit('.extern read_int')

    emit('.section .text')

    for fun_name, fun_instructions in instructions.items():
        emit(f'{fun_name}:')
        emit('pushq %rbp')
        emit('movq %rsp, %rbp')
        emit(f'subq ${locals.stack_used()}, %rsp')

        for insn in fun_instructions:
            emit('# ' + str(insn))
            match insn:
                case ir.Label():
                    emit('')
                    emit(f'.L{insn.name}:')
                case ir.LoadIntConst():
                    if -2**31 <= insn.value < 2**31:
                        emit(f'movq ${insn.value}, {locals.get_ref(insn.dest)}')
                    else:
                        emit(f'movabsq ${insn.value}, %rax')
                        emit(f'movq %rax, {locals.get_ref(insn.dest)}')
                case ir.LoadBoolConst():
                    emit(f'movq ${int(insn.value)}, {locals.get_ref(insn.dest)}')
                case ir.Jump():
                    emit(f'jmp .L{insn.label.name}')
                case ir.CondJump():
                    emit(f'cmpq $0, {locals.get_ref(insn.cond)}')
                    emit(f'jne .L{insn.then_label.name}')
                    emit(f'jmp .L{insn.else_label.name}')
                case ir.Copy():
                    emit(f'movq {locals.get_ref(insn.source)}, %rax')
                    emit(f'movq %rax, {locals.get_ref(insn.dest)}')
                case ir.Call():
                    if (instrinsic := all_intrinsics.get(insn.fun.name)) is not None:
                        args = IntrinsicArgs(
                            arg_refs=[locals.get_ref(a) for a in insn.args],
                            result_register='%rax',
                            emit=emit
                        )
                        instrinsic(args)
                        emit(f'movq %rax, {locals.get_ref(insn.dest)}')
                    else:
                        for i, arg in enumerate(insn.args):
                            register = ['%rdi', '%rsi', '%rdx', '%rcx', '%r8', '%r9'][i]
                            emit(f'movq {locals.get_ref(arg)}, {register}')
                        emit(f'call {insn.fun.name}')
                        emit(f'movq %rax, {locals.get_ref(insn.dest)}')
                case _:
                    raise Exception(f'Unknown instruction: {type(insn)}')

    emit('movq $0, %rax')
    emit('movq %rbp, %rsp')
    emit('popq %rbp')
    emit('ret')
    emit('')

    return "\n".join(assembly_code_lines)

def get_all_ir_variables(instructions: dict[str, list[ir.Instruction]]) -> list[ir.IRVar]:
    result_list: list[ir.IRVar] = []
    result_set: set[ir.IRVar] = set()

    def add(v: ir.IRVar) -> None:
        if v not in result_set:
            result_list.append(v)
            result_set.add(v)

    for fun_instructions in instructions.values():
        for insn in fun_instructions:
            for field in dataclasses.fields(insn):
                value = getattr(insn, field.name)
                if isinstance(value, ir.IRVar):
                    add(value)
                elif isinstance(value, list):
                    for v in value:
                        if isinstance(v, ir.IRVar):
                            add(v)
    return result_list

class Locals:
    """Knows the memory location of every local variable."""
    _var_to_location: dict[ir.IRVar, str]
    _stack_used: int

    def __init__(self, variables: list[ir.IRVar]) -> None:
        self._var_to_location = {}
        self._stack_used = 8
        for v in variables:
            if v not in self._var_to_location:
                self._var_to_location[v] = f'-{self._stack_used}(%rbp)'
                self._stack_used += 8

    def get_ref(self, v: ir.IRVar) -> str:
        """Returns an Assembly reference like `-24(%rbp)`
        for the memory location that stores the given variable"""
        return self._var_to_location[v]

    def stack_used(self) -> int:
        """Returns the number of bytes of stack space needed for the local variables."""
        return self._stack_used