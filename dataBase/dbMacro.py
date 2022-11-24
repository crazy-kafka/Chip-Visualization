from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from LEF.lefPin import LefPin
from .dbBaseObj import DbBaseObj
from .dbTerm import DbTerm


class DbMacro(DbBaseObj):

    def __init__(self, macro_name: str, classType: str, width: float, height: float, pins: List[LefPin], footprint: str, leakage: float):
        super(DbMacro, self).__init__(name=macro_name)
        self.__terms: Dict[str, DbTerm] = {}
        self.__classType = classType
        self.__width = width
        self.__height = height
        self.__area = self.__width * self.__height
        self.__footprint = footprint
        self.__leakage = leakage

        for pin in pins:
            self.__addTerm(pin_name=pin.pin_name, direction=pin.direction, use=pin.use, layer=pin.layer, shape=pin.shape)

    def __addTerm(self, pin_name: str, direction: str, use: str, layer: str, shape: List[Tuple[float, float]]):
        self.__terms[pin_name] = DbTerm(pin_name, direction, use, layer, shape)

    @property
    def classType(self) -> str:
        return self.__classType

    @property
    def terms(self) -> Dict[str, DbTerm]:
        return self.__terms

    @property
    def width(self) -> float:
        return self.__width

    @property
    def height(self) -> float:
        return self.__height

    @property
    def area(self) -> float:
        return self.__area

    @property
    def footprint(self) -> str:
        return self.__footprint

    @property
    def leakage(self) -> float:
        return self.__leakage

    def __repr__(self):
        return f'''
Macro “{self.name}”
    classType: {self.classType}
    width:     {self.__width}
    height:    {self.__height}
    footprint: {self.__footprint}
    numTerms:  {len(self.__terms)}
'''














