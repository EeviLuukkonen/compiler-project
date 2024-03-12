import os
import subprocess
import sys
from dataclasses import dataclass

from compiler.assembler import assemble
from compiler.assembly_generator import generate_assembly
from compiler.ir_generator import generate_ir
from compiler.parser import parse
from compiler.symtab import SymTab, top_level_symtab, root_types
from compiler.tokenizer import tokenize
from compiler.type_checker import typecheck

@dataclass
class _TestCase:
    name: str
    inputs: str
    outputs: list[str]
    program: str


def find_test_cases() -> list[_TestCase]:
    test_cases = []
    test_programs_dir = os.path.join(os.getcwd(), 'test_programs')

    for filename in os.listdir(test_programs_dir):
        if filename.endswith('.txt'):
            testfile = os.path.join(test_programs_dir, filename)
            with open(testfile, 'r') as f:
                content = f.read()
                test_cases_raw = content.split("---")

                test_num = 1
                for case in test_cases_raw:
                    inputs = ""
                    outputs = []
                    program = ""

                    lines = case.split('\n')

                    for line in lines:
                        if line.startswith('prints '):
                            outputs.append(line[7:])
                        elif line.startswith('input '):
                            inputs += f'\\n{line[6:]}'
                        else:
                            program += f'{line}\n'

                    if outputs == []:
                        outputs = ['']

                    test_case = _TestCase(
                        name=f'{filename[:-4]}_{test_num}',
                        inputs=inputs,
                        outputs=outputs,
                        program=program
                    )

                    test_cases.append(test_case)
                    test_num += 1
    return test_cases

for test_case in find_test_cases():
    def run_test_case(test_case: _TestCase = test_case) -> None:
        tokens = tokenize(test_case.program)
        ast_node = parse(tokens)
        typecheck(ast_node, SymTab(locals=dict(top_level_symtab)))
        ir_instructions = generate_ir(root_types, ast_node)
        asm_code = generate_assembly(ir_instructions)
        assemble(asm_code, './compiled_test_program')

        compiled_outputs = subprocess.check_output(
            ['./compiled_test_program'],
            input=test_case.inputs,
            text=True
        ).strip().split('\n')

        assert compiled_outputs == test_case.outputs, f"Test case {test_case.name} failed"

    sys.modules[__name__].__setattr__(
        f'test_{test_case.name}',
        run_test_case
    )
