from __future__ import annotations
from typing import List, Tuple, Dict, Union, Iterable, TYPE_CHECKING, AnyStr

if TYPE_CHECKING:
    pass

from .dbBaseObj import DbBaseObj
from .dbHTerm import DbHTerm
from .dbHInstTerm import DbHInstTerm
from .dbHNet import DbHNet
from .dbInst import DbInst


class DbHInst(DbBaseObj):

    def __init__(self, name: str, cell: str, pHInst: Union[DbHInst, None]):
        super().__init__(name)
        #logical attribute
        self.__cell = cell
        self.__pHInst = pHInst
        self.__hNets: Dict[str, DbHNet] = {}
        self.__hInstTerms: Dict[str, DbHInstTerm] = {}
        self.__hInsts: Dict[str, DbHInst] = {}
        self.__treeHInsts: Dict[str, DbHInst] = {}
        self.__insts: Dict[str, DbInst] = {}
        #physical attribute
        self.__shape: List[Tuple[float, float]] = []
        self.__pt_x = 0.0
        self.__pt_y = 0.0
        self.__origin_x = 0.0
        self.__origin_y = 0.0
        self.__ptn_orient = 'N'
        self.__area = 0.0
        self.__ptn_is_defined = False

    def definePartition(self, shape: List[Tuple[float, float]], pt_x: float, pt_y: float, origin_x: float, origin_y: float, orient: str, area: float):
        if self.__ptn_is_defined is False:
            self.__shape = shape
            self.__pt_x = pt_x
            self.__pt_y = pt_y
            self.__origin_x = origin_x
            self.__origin_y = origin_y
            self.__ptn_orient = orient
            self.__area = area
            self.__ptn_is_defined = True

    def addHNet(self, base_name: str) -> DbHNet:
        hNet_name = f'{self.name}/{base_name}'.lstrip('/')
        if hNet_name not in self.__hNets:
            hNet = DbHNet(name=hNet_name, hInst=self)
            self.__hNets[hNet.name] = hNet
            return self.__hNets[hNet.name]

    def addHInstTerm(self, name: str, direction: str) -> DbHInstTerm:
        hInstTerm = DbHInstTerm(name=name, direction=direction, hInst=self)
        self.__hInstTerms[hInstTerm.name] = hInstTerm
        return hInstTerm

    def addHInst(self, hInst: DbHInst):
        self.__hInsts[hInst.name] = hInst

    @property
    def shape(self) -> List[Tuple[float, float]]:
        return self.__shape

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
        return self.__origin_x, self.__origin_y

    @property
    def origin_x(self) -> float:
        return self.__origin_x

    @property
    def origin_y(self) -> float:
        return self.__origin_y

    @property
    def ptn_orient(self) -> str:
        return self.__ptn_orient

    @property
    def area(self) -> float:
        return self.__area

    @property
    def treeHInsts(self) -> Dict[str, DbHInst]:
        if not self.__treeHInsts:
            self.__traverseTreeHInst(self)
        return self.__treeHInsts

    def __traverseTreeHInst(self, currentHInsts: DbHInst):
        for hInst_name, hInst in currentHInsts.hInsts.items():
            self.__treeHInsts[hInst_name] = hInst
            self.__traverseTreeHInst(hInst)

    @property
    def cell(self) -> str:
        return self.__cell

    @property
    def parent(self) -> DbHInst:
        return self.__pHInst

    @property
    def hInsts(self) -> Dict[str, DbHInst]:
        return self.__hInsts

    @property
    def hInstTerms(self) -> Dict[str, DbHInstTerm]:
        return self.__hInstTerms

    @property
    def hNets(self) -> Dict[str, DbHNet]:
        return self.__hNets

    @property
    def is_ptn(self) -> bool:
        return self.__ptn_is_defined

    @property
    def insts(self) -> Dict[str, DbInst]:
        return self.__insts

    def __repr__(self):
        return f'''
HInst "{self.name}"
    cell     {self.__cell}
    shape    {self.__shape}
    pt_x     {self.__pt_x}
    pt_y     {self.__pt_y}
    origin_x {self.__origin_x}
    origin_y {self.__origin_y}
    orient   {self.__ptn_orient}
    area     {self.__area}
    is_ptn   {self.__ptn_is_defined}
    inst_cnt {len(self.__insts)}
'''











