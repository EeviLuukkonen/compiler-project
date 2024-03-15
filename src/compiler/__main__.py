import sys
from compiler.assembler import assemble
from compiler.assembly_generator import generate_assembly
from compiler.interpreter import interpret
from compiler.ir_generator import generate_ir
from compiler.symtab import SymTab, top_level_symtab, root_types
from compiler.tokenizer import tokenize
from compiler.parser import parse
from compiler.type_checker import typecheck

# TODO(student): add more commands as needed
usage = f"""
Usage: {sys.argv[0]} <command> [source_code_file]

Command 'tokenize':
    Tokenizes source code and prints the tokens.
Command 'interpret':
    Runs the interpreter on source code. Only supports binary operations and if-then-else expressions with literals.
Command 'parse':
    Parses source code and prints the AST.
Command 'typecheck':
    Typechecks source code and prints its result type.
Command 'ir':
    Runs the IR generator on source code and prints the IR instructions.
Command 'asm':
    Generates assembly code from the source code.
Command 'compile':
    Runs all of the steps above and assembles source code into executable machine code file 'compiled_program'.
    See result of compilation by running './compiled_program'.
Common arguments:
    source_code_file        Optional. Defaults to standard input if missing.
 """.strip() + "\n"


def main() -> int:
    command: str | None = None
    input_file: str | None = None
    symtab = SymTab(locals=dict(top_level_symtab))
    for arg in sys.argv[1:]:
        if arg in ['-h', '--help']:
            print(usage)
            return 0
        elif arg.startswith('-'):
            raise Exception(f"Unknown argument: {arg}")
        elif command is None:
            command = arg
        elif input_file is None:
            input_file = arg
        else:
            raise Exception("Multiple input files not supported")

    def read_source_code() -> str:
        if input_file is not None:
            with open(input_file) as f:
                return f.read()
        else:
            return sys.stdin.read()

    if command is None:
        print(f"Error: command argument missing\n\n{usage}", file=sys.stderr)
        return 1

    source_code = read_source_code()
    if command == 'interpret':
        result = interpret(parse(tokenize(source_code)))
        print(result)
    elif command == 'tokenize':
        tokenized_source_code = tokenize(source_code)
        print('\nTokenized source code:\n')
        print("\n".join([str(token) for token in tokenized_source_code]))
    elif command == 'parse':
        parsed_source_code = parse(tokenize(source_code))
        print('\nParsed source code:\n')
        print(parsed_source_code, '\n')
    elif command == "typecheck":
        typechecked_source_code = typecheck(parse(tokenize(source_code)), symtab)
        print('Source code\'s return type:\n')
        print(typechecked_source_code)
    elif command == 'ir':
        tokens = tokenize(source_code)
        ast_node = parse(tokens)
        typecheck(ast_node, symtab)
        ir_instructions = generate_ir(root_types, ast_node)
        for fun, instrs in ir_instructions.items():
            print(f"{fun}:")
            print("\n".join([str(ins) for ins in instrs]))
    elif command == 'asm':
        tokens = tokenize(source_code)
        ast_node = parse(tokens)
        typecheck(ast_node, symtab)
        ir_instructions = generate_ir(root_types, ast_node)
        asm_code = generate_assembly(ir_instructions)
        print(asm_code)
    elif command=='compile':
        tokens = tokenize(source_code)
        ast_node = parse(tokens)
        typecheck(ast_node, symtab)
        ir_instructions = generate_ir(root_types, ast_node)
        asm_code = generate_assembly(ir_instructions)
        assemble(asm_code, 'compiled_program')
    else:
        print(f"Error: unknown command: {command}\n\n{usage}", file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
