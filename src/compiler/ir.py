
from dataclasses import dataclass

@dataclass(frozen=True)
class IRVar:
    name: str

    def __repr__(self) -> str:
        return self.name

@dataclass(frozen=True)
class Instruction():
    """Base class for IR instructions"""

@dataclass(frozen=True)
class Call(Instruction):
    fun: IRVar
    args: list[IRVar]
    dest: IRVar

@dataclass(frozen=True)
class LoadIntConst(Instruction):
    value: int
    dest: IRVar

@dataclass(frozen=True)
class Copy(Instruction):
    source: IRVar
    dest: IRVar
