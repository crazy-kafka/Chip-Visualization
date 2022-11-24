from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    pass

from .dbBaseObj import DbBaseObj


class DbTerm(DbBaseObj):

    def __init__(self, pin_name: str, direction: str, use: str, layer: str, shape: List[Tuple[float, float]]):
        super().__init__(pin_name)
        self.__direction = direction
        self.__use = use
        self.__layer = layer
        self.__shape = shape

    @property
    def direction(self) -> str:
        return self.__direction

    @property
    def use(self) -> str:
        return self.__use

    @property
    def layer(self) -> str:
        return self.__layer

    @property
    def shape(self) -> List[Tuple[float, float]]:
        return self.__shape

    def __repr__(self):
        return f'''
Term "{self.name}"
    direction {self.direction}
    use       {self.__use}
    layer     {self.__layer}
    shape     {self.__shape}
'''


