from __future__ import annotations
from typing import Any, AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    pass

from dataclasses import dataclass

@dataclass
class DbAttribute:
    group_name: str
    attr_name: str
    value: Any
    mode: str

