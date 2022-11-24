from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    pass
from .dbBaseObj import DbBaseObj


class DbVCell(DbBaseObj):

    def __init__(self, name: str):
        super(DbVCell, self).__init__(name=name)


