import re
from typing import Literal, cast, Any
from dataclasses import dataclass

TokenType = Literal['int_literal', 'identifier', 'operator', 'punctuation', 'end']

@dataclass(frozen=True)
class Location:
    line: int
    column: int

    def __eq__(self, other: Any) -> bool:
        if other is L:
            return True

        return (
            self.line == other.line
            and self.column == other.column
        )

L = Location(line=1, column=1)

@dataclass(frozen=True)
class Token:
    text: str
    type: TokenType
    loc: Location

    def __eq__(self, other: Any) -> bool:
        if self.loc == L or other.loc == L:
            return True

        return (
            self.text == other.text
            and self.type == other.type
            and self.loc == other.loc
        )


def tokenize(source_code: str) -> list[Token]:
    token_re = [
        ('newline', re.compile('\n+')), # newline for token line and column
        ( None, re.compile(r'(//|#)[^\n]*|[^\S\n]+')), # comments, whitespaces as None
        ('identifier', re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')),
        ('int_literal', re.compile(r'[0-9]+')),
        ('operator', re.compile(r'==|!=|>=|<=|\+|\-|\*|/|=|<|>|%')),
        ('punctuation', re.compile(r'\(|\)|{|}|\,|;')),
    ]

    position = 0
    line = 1
    column = 1
    tokens = []

    while position < len(source_code):
        for token_type, regex in token_re:
            match = regex.match(source_code, position)
            if match:
                token_text = match.group()

                location = Location(line=line, column=column)

                tokens.append(Token(
                    text=token_text,
                    type=cast(TokenType, token_type),
                    loc=location
                )) if token_type not in [None, 'newline'] else None

                position += len(token_text)
                if token_type == 'newline':
                    line += 1
                    column = 1
                else:
                    column += len(token_text)
                break
        else:
            raise Exception(f"Invalid token near {source_code[position:position+10]}")

    return tokens

if __name__ == "__main__":
    print(tokenize("jee 3 \n +"))