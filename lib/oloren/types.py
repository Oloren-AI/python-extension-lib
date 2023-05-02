from dataclasses import dataclass
from typing import List, Optional, Union

try:
    from py_ts_interfaces import Interface

except ImportError:
    Interface = object


class Type(Interface):
    pass


@dataclass(frozen=True)
class Choice(str, Type):
    choices: List[str]


@dataclass(frozen=True)
class Num(float, Type):
    floating: bool = True
    min_value: Optional[float] = None
    max_value: Optional[float] = None


@dataclass(frozen=True)
class String(str, Type):
    pass


@dataclass(frozen=True)
class File(str, Type):
    allowed_extensions: Optional[List[str]] = None


@dataclass(frozen=True)
class Ty(Interface):
    name: str
    ty: Union[Choice, Num, File]
    type: str


@dataclass(frozen=True)
class Config(Interface):
    name: str
    description: Optional[str]
    args: List[Ty]
    operator: str
    num_outputs: int


# get all subclasses of Type
__all__ = [subclass.__name__ for subclass in Type.__subclasses__()]

if __name__ == "__main__":
    import sys

    path = sys.argv[1]
    with open(path, "r") as f:
        file = f.read()
    with open(path, "w") as f:
        replacement_type = " | ".join([f'"{x}"' for x in __all__])
        # little hacky way of replacing the first instance of "type: string" with with correct string literal
        f.write(file.replace("type: string", "type: " + replacement_type))
