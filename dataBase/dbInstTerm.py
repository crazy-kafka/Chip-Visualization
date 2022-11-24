from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from .dbInst import DbInst
    from .dbTerm import DbTerm
    from .dbNet import DbNet
    from .dbHNet import DbHNet

from utils import CoordinateProcess
from .dbBaseObj import DbBaseObj


class DbInstTerm(DbBaseObj):

    def __init__(self, name: str, inst: DbInst):
        super(DbInstTerm, self).__init__(inst.name + '/' + name)
        self.__inst = inst
        self.__term = inst.cell.terms[name]
        self.__net: Union[DbNet, None] = None
        self.__hNet: Union[DbHNet, None] = None
        self.__shape: List[Tuple[float, float]] = []
        self.__isTieHi = False
        self.__isTieLo = False

    def __setTieHi(self):
        self.__isTieHi = True

    def __setTieLo(self):
        self.__isTieLo = True

    @property
    def isTieHi(self):
        return self.__isTieHi

    @property
    def isTieLo(self):
        return self.__isTieLo

    def __deriveShape(self):
        self.__shape.clear()
        for pt in self.__term.shape:
            self.__shape.append(CoordinateProcess.dbTransform(trans_type='to_global', pt=pt, orient_name=self.__inst.orient, origin=self.__inst.origin))

    def __attachToNet(self, net: DbNet):
        self.__net = net

    def __attachToHNet(self, net: DbHNet):
        self.__hNet = net

    @property
    def hNet(self) -> DbHNet:
        return self.__hNet

    @property
    def isInput(self) -> bool:
        if self.__term.direction == 'INPUT':
            return True
        else:
            return False

    @property
    def isOutput(self) -> bool:
        if self.__term.direction == 'OUTPUT':
            return True
        else:
            return False

    @property
    def term(self) -> DbTerm:
        return self.__term

    @property
    def inst(self) -> DbInst:
        return self.__inst

    @property
    def net(self):
        return self.__net

    def __repr__(self):
        return f'''
InstTerm {self.name}
    isTieHi  {self.isTieHi}
    isTieLo  {self.isTieLo}
    net      {self.net.name if self.net is not None else '""'}
    isOutput {self.isOutput}
    isInput  {self.isInput}
'''






