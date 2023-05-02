from dataclasses import dataclass
from typing import List, Optional, Union

try:
    from py_ts_interfaces import Interface

except ImportError:
    Interface = object


class Type(Interface):
    pass


@dataclass
class choice(Type):
    choices: List[str]


@dataclass
class num(Type):
    floating: bool = True
    min_value: Optional[float] = None
    max_value: Optional[float] = None


@dataclass
class file(Type):
    allowed_extensions: Optional[List[str]] = None


@dataclass
class ty(Type):
    ty: Union[choice, num, file]
