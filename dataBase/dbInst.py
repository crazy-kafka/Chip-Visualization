from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from .dbMacro import DbMacro
    from .dbHInst import DbHInst

from .dbBaseObj import DbBaseObj
from .dbInstTerm import DbInstTerm
from utils import CoordinateProcess, PSTATUS


class DbInst(DbBaseObj):

    def __init__(self, name: str, pHInst: DbHInst, cell: DbMacro, pt_x=0.0, pt_y=0.0, orient='N', pstatus=PSTATUS.UNPLACED):
        super(DbInst, self).__init__(name)
        self.__pHInst = pHInst
        self.__pHInst._DbHInst__insts[name] = self
        self.__cell = cell
        self.__pstatus = pstatus
        self.__pt_x = pt_x
        self.__pt_y = pt_y
        self.__orient = orient

        self.__shape: List[Tuple[float, float]] = []
        self.__origin: Tuple[float, float] = (0.0, 0.0)
        self.__instTerms: Dict[str, DbInstTerm] = {}
        self.__initInstTerms()
        self.__deriveShape()

    def __initInstTerms(self):
        for term_name, term in self.__cell.terms.items():
            if term.use != 'POWER' and term.use != 'GROUND':
                inst_term = DbInstTerm(term_name, self)
                self.__instTerms[inst_term.name] = inst_term

    def __deriveShape(self):
        self.__origin = CoordinateProcess.calculateOriginByOrient(ll_pt=(self.__pt_x, self.__pt_y), orient_name=self.__orient,
                                                                  height=self.__cell.height, width=self.__cell.width)
        macro_shape = [(0, 0), (self.__cell.width, 0), (self.__cell.width, self.__cell.height), (0, self.__cell.height)]
        self.__shape.clear()
        for pt in macro_shape:
            self.__shape.append(CoordinateProcess.dbTransform(trans_type='to_global', pt=pt, orient_name=self.__orient, origin=self.__origin))
        for inst_term in self.__instTerms.values():
            inst_term._DbInstTerm__deriveShape()

    def setPtOrient(self, x: float, y: float, orient: str):
        self.__pt_x = x
        self.__pt_y = y
        self.__orient = orient
        self.__deriveShape()

    def setPt(self, x: float, y: float):
        self.__pt_x = x
        self.__pt_y = y
        self.__deriveShape()

    def setOrient(self, orient: str):
        self.__orient = orient
        self.__deriveShape()

    @property
    def instTerms(self) -> Dict[str, DbInstTerm]:
        return self.__instTerms

    @property
    def orient(self) -> str:
        return self.__orient

    @property
    def cell(self) -> DbMacro:
        return self.__cell

    @property
    def pstatus(self) -> PSTATUS:
        return self.__pstatus

    @property
    def pt(self) -> Tuple[float, float]:
        return self.__pt_x, self.__pt_y

    @property
    def pt_x(self) -> float:
        return self.__pt_x

    @property
    def pt_y(self) -> float:
        return self.__pt_y

    @property
    def origin(self) -> Tuple[float, float]:
        return self.__origin

    @property
    def shape(self) -> List[Tuple[float, float]]:
        return self.__shape















