from __future__ import annotations
from typing import List, Tuple, Dict, Union, Iterable, TYPE_CHECKING, AnyStr

if TYPE_CHECKING:
    pass

from enum import Enum


class PSTATUS(Enum):
    UNPLACED = 0
    PLACED = 1
    FIXED = 2

