from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from .dbNet import DbNet
    from .techLayer import TechLayer

from utils import Print


class DbWire:

    def __init__(self, net: DbNet, layer: TechLayer, from_pt: Tuple[float, float], to_pt: Tuple[float, float], width: float, begin_ext: float, end_ext: float):
        self.__net = net
        self.__from_pt: Tuple[float, float] = from_pt
        self.__to_pt: Tuple[float, float] = to_pt
        self.__length = round(abs(self.__from_pt[0] - self.__to_pt[0]) + abs(self.__from_pt[1] - self.__to_pt[1]), 4)
        self.__layer = layer
        self.__begin_ext = begin_ext
        self.__end_ext = end_ext
        self.__width = width
        if from_pt[0] == to_pt[0]:
            self.__direction = 'VERTICAL'
            begin_ext = begin_ext if from_pt[1] < to_pt[1] else -begin_ext
            end_ext = end_ext if from_pt[1] < to_pt[1] else -end_ext
            self.__shape = [(round(from_pt[0] - width, 4), round(from_pt[1] - begin_ext)),
                            (round(from_pt[0] - width, 4), round(to_pt[1] + end_ext)),
                            (round(to_pt[0] + width, 4), round(to_pt[1] + end_ext)),
                            (round(to_pt[0] + width, 4), round(from_pt[1] - begin_ext))]
        elif from_pt[1] == to_pt[1]:
            self.__direction = 'HORIZONTAL'
            begin_ext = begin_ext if from_pt[0] < to_pt[0] else -begin_ext
            end_ext = end_ext if from_pt[0] < to_pt[0] else -end_ext
            self.__shape = [(round(from_pt[0] - begin_ext, 4), round(from_pt[1] - width)),
                            (round(from_pt[0] - begin_ext, 4), round(to_pt[1] + width)),
                            (round(to_pt[0] + end_ext, 4), round(to_pt[1] + width)),
                            (round(to_pt[0] + end_ext, 4), round(from_pt[1] - width))]
        else:
            Print(f'Invalid from_pt {from_pt} and to_pt {to_pt} from DbWire', level='error')
        self.__net._DbNet__addWire(self)

    @property
    def net(self) -> DbNet:
        return self.__net

    @property
    def layer(self) -> TechLayer:
        return self.__layer

    @property
    def from_pt(self) -> Tuple[float, float]:
        return self.__from_pt

    @property
    def to_pt(self) -> Tuple[float, float]:
        return self.__to_pt

    @property
    def begin_ext(self) -> float:
        return self.__begin_ext

    @property
    def end_ext(self) -> float:
        return self.__end_ext

    @property
    def direction(self) -> str:
        return self.__direction

    @property
    def shape(self) -> List[Tuple[float, float], Tuple[float, float], Tuple[float, float], Tuple[float, float]]:
        return self.__shape

    @property
    def length(self) -> float:
        return self.__length

    def __repr__(self):
        return f'''DbWire
  net_name  {self.net.name}
  layer     {self.layer}
  from_pt   {self.from_pt}
  to_pt     {self.to_pt}
  begin_ext {self.begin_ext}
  end_ext   {self.end_ext}
  direction {self.direction}
  shape     {self.shape}
  length    {self.length}
'''











