from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from .dbHInst import DbHInst
    from .dbHInstTerm import DbHInstTerm
    from .dbHTerm import DbHTerm
    from .dbInstTerm import DbInstTerm
    from .dbNet import DbNet

from .dbBaseObj import DbBaseObj


class DbHNet(DbBaseObj):

    def __init__(self, name: str, hInst: DbHInst):
        super(DbHNet, self).__init__(name)
        self.__hInst = hInst
        self.__hInstTerms: Dict[str, DbHInstTerm] = {}
        self.__hTerms: Dict[str, DbHTerm] = {}
        self.__instTerms: Dict[str, DbInstTerm] = {}
        self.__net: Union[DbNet, None] = None

    @property
    def hInst(self) -> DbHInst:
        return self.__hInst

    def __attachToHInstTerm(self, hInstTerm: DbHInstTerm):
        self.__hInstTerms[hInstTerm.name] = hInstTerm
        hInstTerm._DbHInstTerm__setUpHNet(self)

    def __attachToHTerm(self, hTerm: DbHTerm):
        self.__hTerms[hTerm.name] = hTerm
        hTerm._DbTerm__setDownHNet(self)

    def __setNet(self, net: DbNet):
        self.__net = net
        net._DbNet__addHNet(self)

    @property
    def hTerms(self) -> Dict[str, DbHTerm]:
        return self.__hTerms

    @property
    def hInstTerms(self) -> Dict[str, DbHInstTerm]:
        return self.__hInstTerms

    @property
    def instTerms(self) -> Dict[str, DbInstTerm]:
        return self.__instTerms

    @property
    def net(self) -> DbNet:
        return self.__net


















