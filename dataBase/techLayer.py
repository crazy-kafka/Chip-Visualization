from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    pass
from .dbBaseObj import DbBaseObj


class TechLayer(DbBaseObj):

    def __init__(self, name: str, layer_type: str, direction: str, pitch_x: float, pitch_y: float, width: float, spacing: float, area: float, region: str, based_layer: str, idx: int):
        super(TechLayer, self).__init__(name)
        self.__type = layer_type
        self.__direction = direction
        self.__pitch_x = pitch_x
        self.__pitch_y = pitch_y
        self.__width = width
        self.__spacing = spacing
        self.__area = area

        self.__region = region
        self.__based_layer = based_layer

        self.__idx = idx

    @property
    def idx(self) -> int:
        return self.__idx

    @property
    def type(self) -> str:
        return self.__type

    @property
    def pitch_x(self) -> float:
        return self.__pitch_x

    @property
    def pitch_y(self) -> float:
        return self.__pitch_y

    @property
    def width(self) -> float:
        return self.__width

    @property
    def spacing(self) -> float:
        return self.__spacing

    @property
    def area(self) -> float:
        return self.__area

    @property
    def region(self) -> str:
        return self.__region

    @property
    def basedLayer(self) -> str:
        return self.__based_layer

    def __repr__(self):
        return f'''
Lef Layer {self.name}
    idx         {self.__idx}
    type        {self.__type}
    direction   {self.__direction}
    pitch_x     {self.__pitch_x} 
    pitch_y     {self.pitch_y}
    width       {self.__width}
    spacing     {self.__spacing}
    area        {self.__area}
    region      {self.__region}
    based_layer {self.__based_layer}
'''


