from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from .dbHInst import DbHInst
    from .dbHInstTerm import DbHInstTerm
    from .dbHNet import DbHNet

from .dbBaseObj import DbBaseObj


class DbHTerm(DbBaseObj):

    def __init__(self, name: str, direction: str, hInst: DbHInst, hInstTerm: DbHInstTerm):
        super(DbHTerm, self).__init__(name)
        self.__hInst = hInst
        self.__hInstTerm = hInstTerm
        self.__direction = direction
        self.__downHNet = None

    def __setDownHNet(self, hNet: DbHNet):
        self.__downHNet = hNet

    @property
    def direction(self) -> str:
        return self.__direction

    @property
    def hInstTerm(self) -> DbHInstTerm:
        return self.__hInstTerm

    @property
    def hInst(self) -> DbHInst:
        return self.__hInst

    @property
    def downHNet(self) -> DbHNet:
        return self.__downHNet

    @property
    def upHNet(self) -> DbHNet:
        return self.__hInstTerm.upHNet



