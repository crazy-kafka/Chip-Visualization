from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from .dbInstTerm import DbInstTerm
    from .dbWire import DbWire
    from .dbHNet import DbHNet
from .dbBaseObj import DbBaseObj


class DbNet(DbBaseObj):

    def __init__(self, name: str):
        super(DbNet, self).__init__(name)
        self.__instTerms: Dict[str, DbInstTerm] = {}
        self.__hNets: Dict[str, DbHNet] = {}
        self.__wires: List[DbWire] = []
        self.__length = 0.0

    def __attachToInstTerm(self, inst_term: DbInstTerm):
        self.__instTerms[inst_term.name] = inst_term
        inst_term._DbInstTerm__attachToNet(self)
        self.__hNets[self.name]._DbHNet__attachToInstTerm(inst_term)

    def __addWire(self, wire: DbWire):
        self.__wires.append(wire)
        self.__length = round(self.__length + wire.length, 4)

    def __removeWire(self, wire: DbWire):
        self.__wires.remove(wire)
        self.__length = round(self.__length - wire.length, 4)

    def __addHNet(self, hNet: DbHNet):
        self.__hNets[hNet.name] = hNet

    @property
    def hNets(self) -> Dict[str, DbHNet]:
        return self.__hNets

    @property
    def instTerms(self) -> Dict[str, DbInstTerm]:
        return self.__instTerms

    @property
    def wires(self) -> List[DbWire]:
        return self.__wires

    @property
    def length(self) -> float:
        return self.__length

    def __repr__(self):
        out_str = f'Net {self.name}\n  conn'
        for instTerm in self.instTerms.values():
            if instTerm.isInput:
                out_str += f'\n    -> {instTerm.name}'
            elif instTerm.isOutput:
                out_str += f'\n    <- {instTerm.name}'
        return out_str













