from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from .dbHInstTerm import DbHInstTerm
    from .dbHTerm import DbHTerm
    from .dbHNet import DbHNet
    from .dbVCell import DbVCell
    from .dbInst import DbInst
    from .dbNet import DbNet

from .dbBaseObj import DbBaseObj
from .dbHInst import DbHInst


class DbChip(DbBaseObj):

    def __init__(self, top_name: str):
        super(DbChip, self).__init__(name=top_name)
        self.__hInst = DbHInst(name='', cell=top_name, pHInst=None)
        self.__insts: Dict[str, DbInst] = {}
        self.__nets: Dict[str, DbNet] = {}

    @property
    def insts(self) -> Dict[str, DbInst]:
        return self.__insts

    @property
    def nets(self) -> Dict[str, DbNet]:
        return self.__nets

    @property
    def hInst(self) -> DbHInst:
        return self.__hInst























