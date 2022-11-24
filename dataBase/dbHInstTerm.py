from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from .dbHInst import DbHInst
    from .dbHNet import DbHNet
    import pandas as pd

from .dbBaseObj import DbBaseObj
from .dbHTerm import DbHTerm


class DbHInstTerm(DbBaseObj):

    def __init__(self, name: str, direction: str, hInst: DbHInst):
        super(DbHInstTerm, self).__init__(name=f'{hInst.name}/{name}'.lstrip('/'))
        self.__hInst = hInst
        self.__hTerm = DbHTerm(name=name, direction=direction, hInst=hInst, hInstTerm=self)
        self.__upHNet = None
        self.__pt: Tuple[float, float] = (0.0, 0.0)
        self.__isTieHi = False
        self.__isTieLo = False

        self.io_info: Union[pd.Series, None] = None

    def __setUpHNet(self, hNet: DbHNet):
        self.__upHNet = hNet

    def __setTieHi(self):
        self.__isTieHi = True

    def __setTieLo(self):
        self.__isTieLo = True

    def setPt(self, x: float, y: float):
        self.__pt = (x, y)

    @property
    def isTieHi(self) -> bool:
        return self.__isTieHi

    @property
    def isTieLo(self) -> bool:
        return self.__isTieLo

    @property
    def downHNet(self) -> DbHNet:
        return self.__hTerm.downHNet

    @property
    def upHNet(self) -> DbHNet:
        return self.__hTerm.upHNet

    @property
    def hInst(self) -> DbHInst:
        return self.__hInst

    @property
    def hTerm(self) -> DbHTerm:
        return self.__hTerm

    @property
    def pt(self) -> Tuple[float, float]:
        return self.__pt

    @property
    def pt_x(self) -> float:
        return self.__pt[0]

    @property
    def pt_y(self) -> float:
        return self.__pt[1]


















