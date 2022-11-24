from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    pass


class DbBaseObj:

    def __init__(self, name: str):
        self.__name = name

    @property
    def name(self) -> str:
        return self.__name



